DIST = 0.25/40

def get_encoder(hiplen, encoder):
    def process_encode(encode, key):
        encode_data = {
            "count":[],
            "dist":[],
            "velocity":[],
            "time":[]
        }

        print("Processing...")

        encode[key]["time"] = [round(time_data,1) for time_data in encode[key]["time"]]      
        unique_time_encode = sorted(list(set(encode[key]["time"])))

        for time in unique_time_encode:
            idx = encode[key]["time"].index(time)

            print(idx,"...")

            encode_data["count"].append(encode[key]["count"][idx])
            encode_data["dist"].append(encode[key]["count"][idx]*DIST)
            encode_data["time"].append(encode[key]["time"][idx])

        def cal_gradient(x1, y1, x2, y2):
            return (y2-y1)/(x2-x1)
           
        for idx in range(len(encode_data["dist"])):
            if idx == 0:
                encode_data["velocity"].append(cal_gradient(encode_data["time"][idx+1], encode_data["dist"][idx+1], encode_data["time"][idx], encode_data["dist"][idx]))

            elif idx == (len(encode_data["time"]) - 1):
                encode_data["velocity"].append(cal_gradient(encode_data["time"][idx-1], encode_data["dist"][idx-1], encode_data["time"][idx], encode_data["dist"][idx]))

            else:
                grad_one = cal_gradient(encode_data["time"][idx-1], encode_data["dist"][idx-1], encode_data["time"][idx], encode_data["dist"][idx])
                grad_two = cal_gradient(encode_data["time"][idx+1], encode_data["dist"][idx+1], encode_data["time"][idx], encode_data["dist"][idx])

                encode_data["velocity"].append((grad_one + grad_two)/2)
            
        return encode_data
    
    def process_hiplen(hiplen):
        hiplen_data = {
            "hiplen":[],
            "time":[]
        }

        hiplen["time"] = [round(time_data,1) for time_data in hiplen["time"]]
        unique_time_hiplen = sorted(list(set(hiplen["time"])))

        for time in unique_time_hiplen:
            idx = hiplen["time"].index(time)

            hiplen_data["hiplen"].append(hiplen["hiplen"][idx])
            hiplen_data["time"].append(hiplen["time"][idx])

        return hiplen_data
    
    result = {
        "encoder_one": process_encode(encoder, "encoder_one"),
        "encoder_two": process_encode(encoder, "encoder_two"),
        "hiplen": process_hiplen(hiplen)
    }

    if min(result["hiplen"]["time"]) < min(result["encoder_one"]["time"]):
        result["encoder_one"]["count"].insert(0,0)
        result["encoder_one"]["dist"].insert(0, 0.0)
        result["encoder_one"]["velocity"].insert(0,0.0)
        result["encoder_one"]["time"].insert(0, min(result["hiplen"]["time"]))

        result["encoder_two"]["count"].insert(0,0)
        result["encoder_two"]["dist"].insert(0, 0.0)
        result["encoder_two"]["velocity"].insert(0,0.0)
        result["encoder_two"]["time"].insert(0, min(result["hiplen"]["time"]))

    else:
        result["hiplen"]["hiplen"].insert(0, 0)
        result["hiplen"]["time"].insert(0, min(result["encoder_one"]["time"]))

    result["encoder_one"]["time"] = [(time_data - result["encoder_one"]["time"][0]) for time_data in result["encoder_one"]["time"]]
    result["encoder_two"]["time"] = [(time_data - result["encoder_two"]["time"][0]) for time_data in result["encoder_two"]["time"]]
    result["hiplen"]["time"] = [(time_data - result["hiplen"]["time"][0]) for time_data in result["hiplen"]["time"]]

    return result 