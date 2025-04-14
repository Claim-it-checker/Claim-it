# Advanced Multi-Service Username Validator

**Made by [@newmepe](https://t.me/claim_it_checker) for Breached And Cracked, and niggers looking to snipe cool usernames.**

**Looking for more modules? Join our [Telegram channel](https://t.me/claim_it_checker).**

> **Note**: This is my first tool release, so it’s not perfect. Expect some errors, but I’m working on improvements!

## Overview

The **Advanced Multi-Service Username Validator** is a tool designed to check the availability of usernames across multiple services. It’s built to be extensible, allowing you to add your own checkers, similar to tools like Silver or Open Bullet.

---

## Current Modules

**Modules:**
- Dribble
- Flickr
- Github
- Guns.lol
- Minecraft
- Myspace
- Pastebin
- Reddit
- Roblox
- Snapchat
- Steam
- Telegram
- Vimeo


## How to Use

1. **Add Usernames**:
   - Place the usernames you want to check in the `usernames.txt` file.

2. **Understand Threads**:
   - Each thread checks one username across all services simultaneously.
   - Example: Using 3 threads means 3 usernames are checked at once, with a progress bar for each.

3. **Extensibility**:
   - The tool is designed for customization. You can add your own checkers, as all follow the same format.

4. **Rate Limits**:
   - Services like **GitHub** and **Roblox** may impose rate limits, so use threads wisely to avoid restrictions.

---

## Installation

If you’re braindead follow these steps:

1. **Easy Install**:
   - Run `install.bat` or `install.py` to set up the tool automatically.


## Updates
- New modules will be shared on our[Telegram Channel](https://t.me/claim_it_checker)
Current version: 1.0.0






# Make your own modules
- To make your own .claim config, it must start of with this

checker title: Checker Title
URL: https://url.url
URL_USER: https://website.com/{USERNAME}


- after that, you need to have some result names, like Avaiable, Taken Error etc etc using, Result.name <RESULT NAME>

- then under it, add 4 spaces, then info about how the option is trigerd using the following arguments. 

must_have: (the site must have this plain text)

if_have: (If the site has this plain text)

cant_have: (Plain text the site cant have)

must_have: (Plain text website must have)

code: (ERROR CODE. e.g 200)

if_redirects: true/false 



- for if_have must_have and cant_have, you put plain text there that has to be on the page in <DIV>, like "User Not Found"
