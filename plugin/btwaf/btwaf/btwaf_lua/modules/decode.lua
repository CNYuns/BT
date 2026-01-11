-- decode_ngx.lua - 多层解码器 (使用ngx正则表达式)
-- 支持 base64, url, hex, unicode 解码
-- 自动识别编码类型，最多解码三层

local decode = {}
local bit = require("bit")

-- 预编译正则表达式模式以提高性能
local base64_pattern = "^[A-Za-z0-9+/]*=*$"
local url_pattern = "%[0-9A-Fa-f]{2}"
local hex_pattern = "^[0-9A-Fa-f]*$"
local unicode_pattern = "\\\\u[0-9A-Fa-f]{4}"

-- Base64解码 (使用ngx.decode_base64)
function decode.base64_decode(str)
    if not str or str == "" then
        return nil
    end
    -- 如果是 兼容data:image/jpeg;base64,PD9waHAgcGhwaW5mbygpOz8%2B  data:image/jsp;base64,PD9waHAgcGhwaW5mbygpOz8%2B
    local prefix_match, err = ngx.re.match(str, "^data:[^;]+;base64,","jo")
    if prefix_match then
        str = ngx.re.sub(str, "^data:[^;]+;base64,", "", "jo")
    end
     -- 检查长度是否为4的倍数
    local len = #str
    if len % 4 ~= 0 then
        return nil
    end
    local match, err = ngx.re.match(str, base64_pattern, "jo")
    if not match then
        return nil
    end
    local decoded = ngx.decode_base64(str)
    if decoded==nil then return nil end
    if decode.hex_decode_and_check(decoded) then return decoded end
    return nil
end

function decode.is_visible_char(byte)
    return byte==10 or  byte >= 32 and byte <= 126
end

--url编码
function decode.url_decode(str)
    if not str or str == "" then
        return nil
    end
    local match, err = ngx.re.match(str, url_pattern, "jo")
    if not match then
        return nil
    end
    return ngx.unescape_uri(str)
end

-- 随机取可见字符数
function decode.hex_decode_and_check(decoded)
    if decoded==nil then return false end
    local s,e,f = string.byte(decoded,1,3)
    if s == 31 and  e == 139 and f==8 then
       return decoded
    end
    local sample_data = ""
    local len_decoded=#decoded 
    if len_decoded <=200 then
        sample_data = decoded
    else
        local selected_chars = {}
        local decoded_len = #decoded
        math.randomseed(os.time() + math.random(100000))
        for i = 1, 200 do
            local pos = math.random(decoded_len)
            table.insert(selected_chars, string.sub(decoded, pos, pos))
        end
        sample_data = table.concat(selected_chars)
    end
    local visible_count = 0
    for i = 1, #sample_data do
        
        if decode.is_visible_char(string.byte(sample_data, i)) then
            visible_count = visible_count + 1
        end
    end
    
    local visible_ratio = visible_count / #sample_data
    if len_decoded<=200 then return visible_ratio > 0.85 end 
    return visible_ratio > 0.75
end


-- Hex解码
function decode.hex_decode(str)
    if not str or str == "" then
        return nil
    end
    local len = #str
    if len % 2 ~= 0 then
        return nil
    end
    local match, err = ngx.re.match(str, hex_pattern, "jo")
    if not match then
        return nil
    end
    local result = {}
    local result_len = len / 2
    for i = 1, len, 2 do
        local hex_byte = tonumber(str:sub(i, i+1), 16)
        if not hex_byte then
            return nil
        end
        result[#result + 1] = string.char(hex_byte)
    end
    local result=table.concat(result)
    if decode.hex_decode_and_check(result) then return result end 
    return nil
end

-- Unicode解码
function decode.unicode_decode(str)
    if not str or str == "" then
        return nil
    end
    
    local match, err = ngx.re.match(str, unicode_pattern, "jo")
    if not match then
        return nil
    end
    local result, n, err = ngx.re.gsub(str, "\\\\u([0-9A-Fa-f]{4})", function(m)
        local code = tonumber(m[1], 16)
        if not code then return "" end
        if code < 0x80 then
            return string.char(code)
        elseif code < 0x800 then
            return string.char(0xC0 + bit.rshift(code, 6), 0x80 + bit.band(code, 0x3F))
        else
            return string.char(
                0xE0 + bit.rshift(code, 12),
                0x80 + bit.band(bit.rshift(code, 6), 0x3F),
                0x80 + bit.band(code, 0x3F)
            )
        end
    end, "jo")
    
    return err and nil or result
end

-- 检测编码类型 - 优化检测顺序和逻辑
function decode.detect_encoding(str)
    if not str or type(str)=='string' and str == ""  then
        return nil
    end
    
    local len = #str
    -- 检测Unicode编码 (优先级最高)
    if ngx.re.match(str, unicode_pattern, "jo") then
        return "unicode"
    end
    
    -- 检测URL编码
    if ngx.re.match(str, url_pattern, "jo") then
        return "url"
    end
    
    -- 检测Hex编码 (优化检测逻辑)
    if len >= 2 and len % 2 == 0 then
        local test_str = str
        if str:sub(1, 2) == "0x" then
            test_str = str:sub(3)
        end
        
        if ngx.re.match(test_str, hex_pattern, "jo") and not ngx.re.match(str, "[+/=]", "jo") then
            return "hex"
        end
    end
    
    -- 检测Base64编码
    if len > 0 and len % 4 == 0 and ngx.re.match(str, base64_pattern, "jo") and ngx.re.match(str, "[A-Za-z]", "jo") then
        return "base64"
    end
 
    -- 兼容data:image/jpeg;base64,PD9waHAgcGhwaW5mbygpOz8%2B  data:image/jsp;base64,PD9waHAgcGhwaW5mbygpOz8%2B
    if ngx.re.match(str, "^data:[^;]+;base64,", "jo") then
        return "base64"
    end
    
    if str:sub(1, 1) == "{" and str:sub(-1) == "}" then
        return "json"
    end 
	if str:sub(1, 1) == "[" and str:sub(-1) == "]" then
        return "json"
    end
    -- 检测Gzip压缩 (魔术数字)
    local s,e,f = string.byte(str,1,3)    
    if s == 31 and e == 139 and f==8 then
       return "gzip"
    end

    return nil
end

function decode.json_decode(str)
    -- 验证是否为有效的JSON格式
    if not str or str == "" then
        return nil
    end
    local success, result = pcall(Json.decode, str)
    if not success then
        return nil
    end
    if type(result) ~= "table" then return nil end
    if next(result) == nil then return nil end
    if Public.arrlen(result)==0 then return nil end
    return result
end

function decode.gzip_decode(str)
    local s,e = string.byte(str,1,2)
    if s == 31 or e == 139 then
       local datas=Public.ungzipbit(str)
         return datas
    end
    return nil

end 
-- 单次解码
function decode.decode_once(str)
    local encoding_type = decode.detect_encoding(str)
    if not encoding_type then
        return nil
    end
    
    if encoding_type == "base64" then
        return decode.base64_decode(str)
    elseif encoding_type == "url" then
        return decode.url_decode(str)
    elseif encoding_type == "hex" then
        return decode.hex_decode(str)
    elseif encoding_type == "unicode" then
        return decode.unicode_decode(str)
    elseif encoding_type == "json" then
        return decode.json_decode(str)
    elseif encoding_type == "gzip" then
        return decode.gzip_decode(str)
    end
    
    return nil
end

-- 多层解码主函数
function decode.decode_multi(input_str, max_layers)
    max_layers = max_layers or 3
    
    if not input_str or input_str == "" then
        return nil, {}
    end
    
    local current = input_str
    local decode_path = {}
    local previous_results = {} -- 缓存中间结果，避免重复计算
    
    for layer = 1, max_layers do
        local encoding_type = decode.detect_encoding(current)
        if not encoding_type then
            break
        end
        local decoded = decode.decode_once(current)
        if type(decoded)=='table' then return decoded end 
        if not decoded or decoded == current then
            break
        end
        -- 检查是否出现循环解码
        for i = 1, #previous_results do
            if previous_results[i] == decoded then
                return current, decode_path -- 避免无限循环
            end
        end
        previous_results[#previous_results + 1] = current
        decode_path[#decode_path + 1] = encoding_type
        decoded = ngx.re.gsub(decoded, "^\\s+|\\s+$", "", "jo") 
        current = decoded
    end
    
    return current, decode_path
end

-- 主解码函数 - 优化性能和逻辑
function decode.decode(input_str)
    input_str = ngx.re.gsub(input_str, "^\\s+|\\s+$", "", "jo") 
    if #input_str < 8 then return "" end 
    local result, path = decode.decode_multi(input_str, 3)
    if result==nil then return "" end 
     if type(result)=='table' then return result end 
    if type(result) ~="string" then return "" end 
    if #result ~= #input_str then
        return result
    end
    return ""
end

return decode