# 1. Long Polling vs. Webhooks
- [1. Long Polling vs. Webhooks](#1-long-polling-vs-webhooks)
  - [1.1. Introduction](#11-introduction)
  - [1.2. How Does Polling Work?](#12-how-does-polling-work)
  - [1.3. Long Polling](#13-long-polling)
  - [1.4. How Do Webhooks Work?](#14-how-do-webhooks-work)
  - [1.5. Comparison](#15-comparison)
  - [I Still Have No Idea What to Use](#i-still-have-no-idea-what-to-use)

There are two ways how your bot can receive messages from the Telegram servers. They are called long polling and webhooks.

This section first describes what long polling and webhooks actually are, and in turn outlines some of the advantages and disadvantes of using one or the other deployment method.

## 1.1. Introduction
You can think of the whole webhooks vs. long polling discussion as a question of what deployment type to use. In other words, there are two fundamentally different ways to host your bot (run it on some server), and they differ in the way how the messages reach your bot, and can be processed by PyTelegmraBotAPI (or any other telegam APIs).

This choice matters a lot when you need to decide where to host your bot. For instance, some infrastructure providers only support one of the two deployment types.

Your bot can either pull them in (long polling), or the Telegram servers can push them to your bot (webhooks).

## 1.2. How Does Polling Work?
Imagine you're getting yourself a scoop of ice cream in your trusted ice cream parlor. You walk up to the employee and ask for your favorite type of ice cream. Unfortunately, he lets you know you that it is out of stock.

The next day, you're craving that delicious ice cream again, so you go back to the same place and ask for the same ice cream. Good news! They restocked over night so you can enjoy your salted caramel ice cream today! Yummy.

Polling means that PyTelegramBotAPI proactively sends a request to Telegram, asking for new updates (think: messages). If no messages are there, Telegram will return an empty list, indicating that no new messages were sent to your bot since the last time you asked.

```
______________                                   _____________
|            |                                   |           |
|            |   <--- are there messages? ---    |           |
|            |    ---       nope.         --->   |           |
|            |                                   |           |
|            |   <--- are there messages? ---    |           |
|  Telegram  |    ---       nope.         --->   |    Bot    |
|            |                                   |           |
|            |   <--- are there messages? ---    |           |
|            |    ---  yes, here you go   --->   |           |
|            |                                   |           |
|____________|                                   |___________|
```

It is immediately obvious that this has some drawbacks. Your bot only receives new messages every time it asks, i.e. every few seconds or so. To make your bot respond faster, you could just send more requests and not wait as long between them. We could for example ask for new messages every millisecond! What could go wrong…

Instead of deciding to spam the Telegram servers, we will use long polling instead of regular (short) polling.

## 1.3. Long Polling
Long polling means that PyTelegramAPI proactively sends a request to Telegram, asking for new updates. If no messages are there, Telegram will keep the connection open until new messages arrive, and then respond to the request with those new messages.

Time for ice cream again! The employee already greets you with your first name by now. Asked about some ice cream of your favorite kind, the employee smiles at you and freezes. In fact, you don't get any response at all. So you decide to wait, firmly smiling back. And you wait. And wait. Some hours before the next sunrise, a truck of a local food delivery company arrives and brings a couple of large boxes into the parlor's storage room. They read ice cream on the outside. The employee finally starts to move again. “Of course we have salted caramel! Two scoops with sprinkles, the usual?” As if nothing had happened, you enjoy your ice cream while leaving the world's most unrealistic ice cream parlor.

```
______________                                   _____________
|            |                                   |           |
|            |   <--- are there messages? ---    |           |
|            |   .                               |           |
|            |   .                               |           |
|            |   .     *both waiting*            |           |
|  Telegram  |   .                               |    Bot    |
|            |   .                               |           |
|            |   .                               |           |
|            |    ---  yes, here you go   --->   |           |
|            |                                   |           |
|____________|                                   |___________|
```

> Note that in reality, no connection would be kept open for hours. Long polling requests have a default timeout of 30 seconds (in order to avoid a number of technical problems). If no new messages are returned after this period of time, then the request will be cancelled and resent—but the general concept stays the same.

Using long polling, you don't need to spam Telegram's servers, and still you get new messages immediately! Nifty.

## 1.4. How Do Webhooks Work?
After this terrifying experience (a whole night without ice cream!), you'd prefer not to ask anyone about ice cream at all anymore. Wouldn't it be cool if the ice cream could come to you?

Setting up a webhook means that you will provide Telegram with a URL that is accessible from the public internet. Whenever a new message is sent to your bot, Telegram (and not you!) will take the initiative and send a request with the update object to your server. Nice, heh?

You decide to walk to the ice cream parlor one very last time. You tell your friend behind the counter where you live. He promises to head over to your apartment personally whenever new ice cream is there (because it would melt in the mail). Cool guy.

```
______________                                   _____________
|            |                                   |           |
|            |                                   |           |
|            |                                   |           |
|            |         *both waiting*            |           |
|            |                                   |           |
|  Telegram  |                                   |    Bot    |
|            |                                   |           |
|            |                                   |           |
|            |    ---  hi, new message   --->    |           |
|            |   <---    thanks dude     ---     |           |
|____________|                                   |___________|
```

## 1.5. Comparison
The main advantage of long polling over webhooks is that it is simpler. You don't need a domain or a public URL. You don't need to fiddle around with setting up SSL certificates in case you're running your bot on a VPS. Use bot.start() and everything will work, no further configuration required. Under load, you are in complete control of how many messages you can process.

Places where long polling works well include:

- During development on your local machine.
- On majority of servers.
- On hosted "backend" instances, i.e. machines that actively run your bot 24/7.
The main advantage of webhooks over long polling is that they are cheaper. You save a ton of superfluous requests. You don't need to keep a network connection open at all times. You can use services that automatically scale your infrastructure down to zero when no requests are coming. If you want to, you can even make an API call when responding to the Telegram request, even though this has a number of drawbacks.

Places where webhooks work well include:

- On servers with SSL certificates.
- On hosted "frontend" instances that scale according to their load.
- On serverless platforms, such as cloud functions or programmable edge networks.

## I Still Have No Idea What to Use
Then go for long polling. If you don't have a good reason to use webhooks, then note that there are no major drawbacks to long polling, and—according to our experience—you will spend much less time fixing things. Webhooks can be a bit nasty from time to time (see below).

Whatever you choose, if you ever run into serious problems, it should not be too hard to switch to the other deployment type after the fact. With grammY, you only have to touch a few lines of code. The setup of your middleware is the same.
