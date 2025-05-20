# Tangram Web

This is part of the https://github.com/alf-labs/tangram
project.


## Requirements

The project uses [Node.js](https://nodejs.org/) version 24.

If you do not have Node.js installed, you can install it:
* Directly from https://nodejs.org/
* Via the [FNM node manager](https://github.com/Schniz/fnm)
* Via the [NVM node manager](https://github.com/nvm-sh/nvm)

"Node managers" allow you to have different versions of Node.js
installed on your system and switch easily between projects.
NVM is sort of the "legacy original" node manager, and FNM is
a newer implementation.
 
If you're using Linux, MacOS, or Windows via PowerShell or
MSYS/Cygwin/Git Bash, consider using FNM.

If you're using Windows via CMD console, NVM is probably a
better fit.


## IDE

The project should work fine out of the box with either VS Code
or WebStorm.

When using FNM, WebStorm may fail to find the proper Node.js
binary to use. That's because it looks at it in the `PATH`,
yet FNM does not install any Node.js in the global `PATH`,
only  in sub-shells. You can manually run `fnm env` to find
the current Node.js binary `PATH` and update WebStorm to use
that, or you can start WebStorm from a shell where you already
executed `fnm use`, thus ensuring the `PATH` is already set
before  WebStorm inherits it.


## Dev vs Deployment

This project contains a `.nvmrc` file. If you're using FNM
or NVM, you can activate the proper version of Node.js first:

```shell
$ fnm use
or
$ nvm use
```

Then install the required node packages once:
```shell
$ npm install
```

To build and run the Dev profile:
```shell
$ npm dev
```

The `dev` version uses the Vite shell.
Press "o" to open the site in your current web browser instance.
In dev mode, this has hot reload, or use "r" to force reload.


To build for the Prod profile:
```shell
$ npm run build
optional:
$ npm run preview
```

`preview` runs the Vite shell to preview it locally.


## License

[MIT license](../LICENSE).




~~
