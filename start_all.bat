@echo off
start "Auth" cmd /k "cd /d F:\ICTBD_02\PycharmProjects\passport-portal\auth-service && C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe app.py"
start "Application" cmd /k "cd /d F:\ICTBD_02\PycharmProjects\passport-portal\application-service && C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe app.py"
start "Status" cmd /k "cd /d F:\ICTBD_02\PycharmProjects\passport-portal\status-service && C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe app.py"
start "Admin" cmd /k "cd /d F:\ICTBD_02\PycharmProjects\passport-portal\admin-service && C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe app.py"
timeout /t 3
start "Gateway" cmd /k "cd /d F:\ICTBD_02\PycharmProjects\passport-portal\api-gateway && C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe app.py"
