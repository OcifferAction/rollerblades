# Rollerblades

## Plex preroll automatic rotation script

You've spent all that time building up your Plex library, so you decide you want to play around with some of Plex's fun features, like prerolls. But before long, you're bored with seeing the same clip every time, right? So, you find another and change it up. Then you find another, and another, and another.

Before long, you're in the Plex settings messing around with preroll every other day, and honestly? It's a pain in the rear, so you'd like to automate changing these prerolls. Maybe a regular rotation. But wait, there are special holiday prerolls you like too, and there's that fun April Fool's Day one as well that you pranked your family with. How do you keep up with all of these?

Yes, there's [another solution](https://github.com/TheHumanRobot/Rollarr) out there already. I tried it, and while yes, it sure does look really impressive, honestly, I couldn't get it to work reliably. For *me*, it literally worked once. Four hours of bashing my head against the table later, I gave up and started writing this. Now call me biased, but in the end, I like this better. Sure, the other tool has a fancy web UI, but this is small, tight, and just works - for me at least. Maybe the other thing works for everyone else, and I'm some kind of knucklehead. If that's the case, I'll own that. This also runs as a Docker container, which for me is no big deal, since I've already got a load of other Docker containers running on systems. What's one more? Let's get to the "how" part.

## Find Your Plex Token

This is the hardest part, and honestly, it's not hard. Go into the Plex Web UI, pull up any movie or episode of a show, hit the 3-dots button (More), then Get Info. This brings up the Media Info screen, with all the details about your media file, with all the specifics, down to video and audio codecs, etc. In the bottom left corner of that window, there's a link that says, "View XML". Click it. Your browser will pop open a new tab with a bunch of XML. Copy the URL from your browser and paste it into a text editor somewhere. You're looking for the very end of the URL. It will say, "X-Plex-Token=[bunch of text]". You're interested in the bunch of text after the equals sign. Make a note of this - this is the Plex Token. You'll need this later when you go to instantiate your container.

## Create your Config File

This might seem a little daunting if you've never created JSON (Javascript Object Notation) formatted text before, but it's really not so bad. You'll be a pro in no time, especially if you've ever written Python code. You'll want sections for the SPECIAL_MONTHS, HOLIDAYS, and DAILYPATH areas. Here's the default config for an example:

{
    "SPECIAL_MONTHS": {
		"October": "/media/prerolls/Halloween_Spider.mp4;/media/prerolls/Halloween_Spooky.mp4;/media/prerolls/Halloween_Vampire_Bats.mp4;/media/prerolls/Halloween.mp4",
		"December": "/media/prerolls/Christmas_Tree_Magic.mp4;/media/prerolls/Christmas_Tree.mp4;/media/prerolls/Christmas.mp4"
    },
    "HOLIDAYS": {
		"0214": "/media/prerolls/Valentine's_Day_Flowers.mp4;/media/prerolls/Valentine's_Day_Hearts.mp4"
		"0216": "/media/prerolls/Mardi_Gras.mp4",
		"0217": "/media/prerolls/Mardi_Gras.mp4",
		"0218": "/media/prerolls/Mardi_Gras.mp4",
		"0219": "/media/prerolls/Mardi_Gras.mp4",
		"0220": "/media/prerolls/Mardi_Gras.mp4",
		"0221": "/media/prerolls/Mardi_Gras.mp4",
		"0222": "/media/prerolls/Mardi_Gras.mp4",
        "0401": "/media/prerolls/April_Fools_FBI.mp4;/media/prerolls/April_Fools_PlexHub.mp4",
		"0408": "/media/prerolls/Easter.mp4",
		"0409": "/media/prerolls/Easter.mp4",
		"0701": "/media/prerollss/Independence1.mp4;/media/prerollss/Independence2.mp4",
		"0702": "/media/prerollss/Independence1.mp4;/media/prerollss/Independence2.mp4",
		"0703": "/media/prerollss/Independence1.mp4;/media/prerollss/Independence2.mp4",
		"0704": "/media/prerollss/Independence1.mp4;/media/prerollss/Independence2.mp4",
		"1115": "/media/prerolls/Thanksgiving.mp4",
		"1116": "/media/prerolls/Thanksgiving.mp4",
		"1117": "/media/prerolls/Thanksgiving.mp4",
		"1118": "/media/prerolls/Thanksgiving.mp4",
		"1119": "/media/prerolls/Thanksgiving.mp4",
		"1120": "/media/prerolls/Thanksgiving.mp4",
		"1121": "/media/prerolls/Thanksgiving.mp4",
		"1122": "/media/prerolls/Thanksgiving.mp4",
		"1123": "/media/prerolls/Thanksgiving.mp4",
		"1124": "/media/prerolls/Thanksgiving.mp4"
    },
    "DAILYPATH": "/media/prerollss/Norm_Anywhere.mp4;/media/prerollss/Norm_ChrisFlix.mp4;/media/prerollss/Norm_Elegant_Short.mp4"
}

The default config has a month for Halloween and a month for Christmas. Valentine's Day and April Fools have single days. The others have multiple days that can be configured or removed.

## Launching the Container

If you're the launching from CLI type, you'll need to make a directory for your config file, drop that on the host, and then instantiate your container. For our purposes here, I'm going to assume you decided to stick your files in a directory called `/var/docks/rollerblades`. You can put your files whereever you feel like though. You do you. Also, be safe - don't run this thing as root. There's really no need to. You don't need any sort of special priviliges to run this, so I'm going to assume you're going to run this as your regular user. Figure out your user's UID and GID value. To get this most easily, jump into the terminal and type `id`. The first two things to come back will be your UID and GID values. Note these as well.

Ready? You'll of course, need to know the URL scheme (http/https), hostname, port (if it's different than 32400), your Plex token that you figured out above, the path to your config file (from the perspective of the container, if not `/config/prerolls.json`), if you intend to turn off the Pride Month feature, how often you want to sync the preroll setting (default is hourly), and if you need to turn on debugging. Here's a sample invocation:

```bash
docker run -d \
    --name=rollerblades \
    --restart=unless-stopped \
    --user=1000:1000 \
    -v /var/docks/rollerblades:/config \
    -e HOST=*ENTER YOUR PLEX IP* \
    -e TOKEN=*ENTER YOUR PLEX TOKEN* \
    ocifferaction/rollerblades:latest
```

Personally, I prefer to run using `docker-compose`. I run my instance as part of a stack in Portainer, but as always, you do you. Here's an example `docker-compose` file you could use:

```yaml
---
version: '3'

services:
  rollerblades:
    image: ocifferaction/rollerblades:latest
    container_name: rollerblades
    volumes:
      - /var/docks/rollerblades:/config
    environment:
      - HOST=*ENTER YOUR PLEX IP*
      - TOKEN=*ENTER YOUR PLEX TOKEN*
    restart: unless-stopped
    user: 1000:1000
    network_mode: bridge
```

You'll note in both of these examples, I'm leveraging many of the defaults - https, port 32400, the 3600s sync interval, leaving October and December activated, default location for config file, etc. That's why so few options in use.
