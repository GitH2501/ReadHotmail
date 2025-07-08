from fastapi.responses import JSONResponse
from models.model import Model

model = Model()


def paginate_task(request, page, total, limit):
    
    # offset = max(total - limit, 0)
    offset = (page - 1) * limit
    # end = start + limit

    data_table = model.getProfilePage(limit, offset)
    # print(data_table[start:end])
    # 
    # fix_data = []
    
    # for i in range(total):
        
    #     fix_data.append(
    #          {
    #             "ID":"2025",
    #             "Profile_name":"vannam3002@gmail.com",
    #             "Browser":"Chrome",
    #             "Proxy_Ip": "192.168.1.20",
    #             "Proxy_port": "5000",
    #             "Proxy_user": "proxy",
    #             "Proxy_pass": "proxy",
    #             "Access_token":"Null",
    #             "Status":"Completed"
    #         },
    #     )
    
    # table_data = fix_data[start:end]
    
    return JSONResponse(
        content={
            "result":data_table
        }
    )