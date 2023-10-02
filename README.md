# install

Fetch the `my-epitech-relay` submode and copy it to the `install` folder.

```sh
git submode update --init
cp my-epitech-relay install
```

In this folder, you need to setup the `.env` file properly.

```
cp .env.example .env
```

Set the `BROWSER_BINARY_PATH`. For instance:
> `BROWSER_BINARY_PATH=/nix/store/.../bin/chromium`

Install the node dependancy, build and run the server:
```
npm install
npm run build
npm run start
```

If this is the first time you run it, it might show your a login window.
Now you can run the `python main.py` script to fetch the last report update.

