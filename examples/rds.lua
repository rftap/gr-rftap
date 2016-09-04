-- lua wireshark dissector for RDS (Radio Data System)

-- put this file in: ~/.config/wireshark/plugins/rds.lua
-- or in (old location): ~/.wireshark/plugins/rds.lua

-- Specifications: http://www.nrscstandards.org/sg/nrsc-4-b.pdf
-- https://en.wikipedia.org/wiki/Radio_Data_System

rds_proto = Proto("rds","Radio Data System (RDS)")

local f_pi = ProtoField.uint16("rds.pi", "PI code", base.HEX, nil, nil, "Program Identification (PI) code")
local f_group_type = ProtoField.uint16("rds.group", "Group type code", base.DEC, nil, 0xf000, "Group type code (0-15)")
local f_version_code = ProtoField.uint16("rds.version", "Version code", base.DEC, nil, 0x0800, "Version code (A=0, B=1)")
local f_af1 = ProtoField.uint8("rds.af1", "AF1 code", base.DEC, nil, nil, "First Alternate Frequency (AF) code")
local f_af2 = ProtoField.uint8("rds.af2", "AF2 code", base.DEC, nil, nil, "Second Alternate Frequency (AF) code")
local f_altfreq = ProtoField.float("rds.altfreq", "Alternate Frequency", "Alternate Frequency for this station")

rds_proto.fields = {f_pi, f_group_type, f_version_code, f_af1, f_af2, f_altfreq}

function rds_proto.dissector(tvb,pinfo,tree)

    pinfo.cols.protocol:set("RDS")
    pinfo.cols.info:set("")
    local t = tree:add(rds_proto,tvb:range(0,12))

    -- Program Identification (PI), aka station ID
    local pi_code = tvb:range(0,2):uint()
    t:add(f_pi, tvb:range(0,2))

    -- RDS frame type and version
    local group_type = tvb:range(2,2):bitfield(0,4)
    t:add(f_group_type, tvb:range(2,2))
    local version_code = tvb:range(2,2):bitfield(4,1)
    t:add(f_version_code, tvb:range(2,2))

    -- Wireshark INFO column
    local s = string.format('PI=%04X GRP=%u%s', pi_code, group_type, (version_code==0 and 'A' or 'B'))
    pinfo.cols.info:append(s)

    -- Add station name to INFO column
    if group_type == 0 then
        local name_fragment = tvb(6,2):string()
        pinfo.cols.info:append(' <' .. name_fragment .. '>')
    end

    -- helper function for decoding Alternate Frequency code
    local function decode_altfreq(offset)
        local af = tvb:range(offset,1):uint()
        if af > 0 and af <= 204 then
            local freq_Hz = 87.6e6 + 0.1e6*(af-1)  -- for field value
            local freq_MHz = freq_Hz/1e6+0.01  -- for display

            -- add Alternate Frequency field
            s = string.format('Alternate Frequency: %.1f MHz', freq_MHz)
            t:add(f_altfreq, tvb:range(offset,1), freq_Hz, s)

            -- Add Alternate Frequency to INFO column
            pinfo.cols.info:append(string.format(' AF=%.1fMHz', freq_MHz))
        end
    end

    -- Decode Alternate Frequency fields
    if group_type == 0 and version_code == 0 then
        t:add(f_af1, tvb:range(4,1))
        decode_altfreq(4)
        t:add(f_af2, tvb:range(5,1))
        decode_altfreq(5)
    end
end
