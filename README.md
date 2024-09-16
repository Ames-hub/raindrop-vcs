<h1 align="center">
Raindrop VCS

![License](https://img.shields.io/badge/license-CC_1.0-yellow)
![Python](https://img.shields.io/badge/Python-3.11.9-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Required-blue)
![Postgre](https://img.shields.io/badge/PostgreSQL-Required-blue)
</h1>

# What is Raindrop?
Raindrop is a decentralised Version Control System (VCS), similar to GitHub.<br>
However, unlike GitHub, we are completely free, and we offer no premium features<br>
because all features are available to all. So this means no project size limits on private repositories one.<br>

It is also inspired by Jetbrains Space, which is a program I saw which looked very
handy but was only available for certain groups/people. So in future implementations, I may be making my own free 
version of it here.

This is a tool primarily meant for developers, but could be used by anyone.<br>

# Features / Roadmap
Raindrop has/will have the following features: <br>

**Implemented**
- [x] Plugin Support
- [x] Docker Integration
- [x] Built-in WebUI
- [x] Built-in API
- [x] Optional Built-in Database

**Unimplemented**
- [ ] Pushing code
- [ ] Pulling code
- [ ] Branching
- [ ] Merging
- [ ] Code Review
- [ ] Issue Tracking

**Note, as Raindrop is hosted by different individuals, the features may vary between servers<br>
As some may be out of date or have had completely disabled the feature.**

## Usage of Raindrop
Raindrop, unlike Git which uses the terminal, primarily uses a WebUI.<br>
So you can use Raindrop from any device, as long as you have a browser.

Either the person hosting Raindrop for you will provide you with a link, or you can host it yourself<br>
and Raindrop will tell you the link there.<br>

To those hosting Raindrop, I encourage you to visit the docs/hosting.md file for more information.<br>
This will contain detailed, step-by-step installation data for Linux and Windows 10+ and other useful information.

## How does it work?
Raindrop uses practically the same system that GitHub uses.<br>
It uses a database to store all the data, and then it uses a server to host the data.<br>

This has been a simple overview<br>
For further details, see the docs/vcs.md file.