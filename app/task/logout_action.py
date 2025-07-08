import logging
from fastapi import Request
from fastapi.responses import JSONResponse

def logout_task(request: Request):
    try:
        if hasattr(request, "session") and isinstance(request.session, dict):
            print("===> Có session, tiến hành clear")
            request.session.clear()
        else:
            print("===> Không có session hoặc session không hợp lệ")

        return JSONResponse(
            content={
                "logout": "success",
                "message": "Đăng xuất thành công"
            }
        )

    except Exception as e:
        print(f"===> Lỗi khi logout: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "logout": "error",
                "message": f"Lỗi khi đăng xuất: {str(e)}"
            }
        )
