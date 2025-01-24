for /L %%i in (1,1,254) do (
ping -a -n 1 192.168.1.%%i 
)

arp -a >con