![MedBlocks Logo](https://i.imgur.com/Dx4LfC2.png)

With Medblocks you can store your medical records (and other documents actually) securely on the IPFS. It will have a reference of it on BigChainDB with permission keys, so you can comtrol who has access to your data.

## Installation
MedBlocks works perfectly on Linux. It should work on windows, but I haven't tested it because some of the dependencies required build tools for windows (which was a pain to install)

1. Install Docker and docker-compose
2. Clone the repository
```
git clone https://github.com/sidharthramesh/medblocks.git
cd medblocks

```
3. Build docker image
```
docker-compose build .
```
4. Run image
```
docker-compose run server
```
5. Test version
```
# python medblocks.py --version
```

The working of medblocks is explained in detail in this [article]().

Also check out this video demonstration for more clarity:

[Video Demonstration](https://www.youtube.com/watch?v=5R-0eyWU99I)
