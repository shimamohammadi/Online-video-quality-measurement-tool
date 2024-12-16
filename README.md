# QualityPulse

![Framework](src/QualityPulse.jpg)

<p align="justify">
QualityPulse is an innovative interface designed to monitor video quality in real time, inspired by the way an electrocardiogram visualizes heart activity. The system evaluates video quality on a scale from 0 to 100, with 100 representing the highest quality.
The model is trained using the VMAF quality metric and bitstream features (e.g., quantization parameter) extracted from H.265 videos. Users can upload videos in the .m3u8 format or evaluate live streaming videos directly from Channel 3 of Iranian Broadcasting TV.
This interface simplifies quality evaluation, particularly for streaming applications, by providing a visual and intuitive representation of video performance
Demonstrating the quality of streams  as it plays 
<p>

This tool supports different protocols like RTP, RTMP as well as TCP based protocols such as HLS.
Since most of these streams are based on h.264, the tool receives the packets and fragments it without any transcoding.

In the textbox paste the URL of an m3u8 files or check the Irib radio button.
-The Irib is Iranaian channel 3.

This tool is capable of analyzing both the UDP and TCP.
It works in realtime.

Different parameters are extracted from video's bitsream

Press Stop button to end the process.

Make sure to delete all the .yuv and .264 files before start again.( you can use batch files in order to accomplish it )

See one screen of the tool at "watch me" file
