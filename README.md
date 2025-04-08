# CLUB2

**CLUB2** - a simple CLI-chat. Consists of two servers:  
1. *Display server* - here all the messages from all users are displayed.
2. *Receive server* - receives user messages.

The key feature of CLUB2 is that you only need `nc` to connect.

### How to host?

You can launch CLUB2 servers with this command:

```
python main.py
```

Yeah, it is that simple! You don't even need to install external modules via pip or create a virtual environment.

You can also run CLUB2 in a container:
1. Build:
```
docker build . -t club2
```
2. Run:
```
docker run --rm --network="host" club2
```

After a successful launch, make sure both display and receive servers are accessible to your clients.

### How to use?

After the CLUB2 is hosted by you or someone else, you are ready to connect. We assume that you are using `nc`, but some other clients are also suitable, so it is for you to choose.

It is important to note that two separate terminals for two servers are used for connection, respectively. Therefore, it is convenient to use `tmux`, `terminator` or analogues.

Focuse on the first window and connect to the *display server*:
```
nc <IP> 31337
```
Focuse on the second window and connect to the *receive server*:
```
nc <IP> 31338
```

You are ready to go! Now you are allowed to type and send messages in the second window.

> Notice that you need to press Enter twice to send the message. This feature allows users to send multiline messages.
