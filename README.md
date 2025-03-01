# TikTokGenerator
The main goal of the project is to create a generative AI-based system for generating short videos on a given topic.

#### List of channels using this tool
- https://www.youtube.com/@AviationFeed_27

## Flow
Overall conception looks basicly like this:
1. Write script for a video
2. Convert to audio
3. Find base videos
4. Generate video (concatenate base videos, add audio and subtitles)

As the most challenging part is to find quality base videos, which will reflect the content of the script, the project was splitted into to parts.

### Base videos store
Scrapes free base videos from the web, generates descriptions and stores embedding of each one in the vector store.


### Videos generator
Generates script and audio, finds most suitable base videos and creates final video from them.

![Untitled Diagram drawio-2](https://github.com/user-attachments/assets/f774ee55-95f0-4ba5-897a-caf43fde23d4)

