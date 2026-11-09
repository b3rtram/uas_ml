"""MESSAGING: send and receive events over NATS JetStream. (Same file in backend/ and ml_service/.)
JetStream stores every event in a stream: if a receiver is down, its events wait until it is back."""
import json
import os

import nats

NATS_URL = os.getenv("NATS_URL", "nats://127.0.0.1:4222")
STREAM = "STOCK"
SUBJECTS = ["prices.updated", "predictions.created"]       # the two kinds of events in our app

nc = None                                                  # the connection to the NATS server
js = None                                                  # its JetStream part (stored events)


async def connect():
    global nc, js
    nc = await nats.connect(NATS_URL)
    js = nc.jetstream()
    await js.add_stream(name=STREAM, subjects=SUBJECTS)    # create the stream; the same config again is fine


async def publish(subject, event):
    await js.publish(subject, json.dumps(event).encode())  # dict -> JSON -> bytes


async def subscribe(subject, group, handler):
    """Call handler(event) for every event on subject.
    group = name under which NATS remembers what we have processed. Several programs with the same
    group share the events (each event goes to one of them): start a second ML service = twice the speed."""
    async def on_message(msg):
        await handler(json.loads(msg.data))
        await msg.ack()                                    # done: don't deliver this event to us again

    await js.subscribe(subject, queue=group, durable=group, cb=on_message, manual_ack=True)


async def close():
    await nc.drain()                                       # finish open messages, then disconnect
