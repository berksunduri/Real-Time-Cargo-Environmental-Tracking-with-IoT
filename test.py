import json
import zstandard
import bz2
import lzma


message = {
    "latitude": 42.724601923423705,
    "longitude": 42.724601923423705,
    "temperature": 25.712312412342134,
    "humidity": 48.712312412342134,
    "acceleration": 5.712312412342134,
    "gyro": {"x": 0.712312412342134, "y": 0.712312412342134, "z": 0.712312412342134}
}

message_str = json.dumps(message)

# Compress the string using zstd
cctx = zstandard.ZstdCompressor()
compressed_message = cctx.compress(message_str.encode())
bz2_message = bz2.compress(message_str.encode())
xz_message = lzma.compress(message_str.encode())

print("Size of the uncompressed message (in bytes):", len(message_str.encode()))
print("Size of the ZSTD compressed message (in bytes):", len(compressed_message))
print("Size of the BZ2 compressed message (in bytes):", len(bz2_message))
print("Size of the XZ compressed message (in bytes):", len(xz_message))

