import cv2
import asyncio
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling, add_signaling_arguments

class VideoStreamTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        frame_ready, frame = self.cap.read()
        if not frame_ready:
            return None
        return frame

async def run(pc, signaling):
    @pc.on("track")
    async def on_track(track):
        print("Receiving track:", track.kind)

    # Create webcam track
    local_video = VideoStreamTrack()
    pc.addTrack(local_video)

    await signaling.connect()
    offer = await signaling.receive()
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await signaling.send(pc.localDescription)

    await signaling.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="WebRTC webcam streamer")
    add_signaling_arguments(parser)
    args = parser.parse_args()

    signaling = TcpSocketSignaling("localhost", 8080)
    pc = RTCPeerConnection()

    asyncio.run(run(pc, signaling))
