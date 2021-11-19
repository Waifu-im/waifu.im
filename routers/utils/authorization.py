from fastapi import FastAPI,HTTPException,Depends,Header,Request
from itsdangerous import URLSafeSerializer, BadSignature
"""Token verification"""

async def is_valid_token(request:Request,authorization: str = Header(None),request_perms : int=None):
    if not authorization:
        raise HTTPException(status_code=401,detail="No Token, please check that you provided a Token and that your correctly formated it in the Authorization header.")
    try:
        token = authorization.split(" ")[1]
        rule = URLSafeSerializer(request.app.state.secret_key)
        info=rule.loads(token)
        user_secret=info.get("secret")
        user_id=int(info.get('id'))
    except (TypeError,KeyError,AttributeError,IndexError,BadSignature):
        raise HTTPException(status_code=403,detail=f"Invalid Token, please check that you did correctly format it in the Authorization header and that the token is up to date.")

    else:
        if request_perms:
            perm_name="access_galleries"
            authorized=await request.app.state.pool.fetchrow('SELECT Registered_user.is_admin,Permissions.page FROM Registered_user LEFT JOIN Permissions ON Permissions.user_id=Registered_user.id WHERE Registered_user.id=$1 and Registered_user.secret=$2 and (Permissions.page=$3 or Registered_user.is_admin) ',user_id,user_secret,perm_name)
        else:
            authorized=await request.app.state.pool.fetchrow('SELECT id,is_admin from Registered_user WHERE id=$1 and secret=$2 ',user_id,user_secret)
        if authorized:
            return info
        else:
            raise HTTPException(status_code=403,detail=f"Invalid Token, You do not have the permissions to request this route please check that the token is up to date{' and, as you requested the id url parameter that you have the permissions to do so' if request_perms else ''}.")
