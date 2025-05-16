# Tangram Rust Generator

This is a Rust version of the Python Tangram Generator.


## Requirements

Currently based on Rust 1.86, 2024 edition.

- Windows: Use `rustup` as explained in [rustup.rs](https://rustup.rs/).
- Debian 13 (testing): Use `apt install rustup`.
- Debian 12 (stable):  Manually install `rustup` as explained in
  [installation methods](https://forge.rust-lang.org/infra/other-installation-methods.html):
```
$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs
or
$ wget -O rustup-init.sh https://static.rust-lang.org/rustup/rustup-init.sh
$ chmod +x rustup-init.sh
$ ./rustup-init.sh
$ . "$HOME/.cargo/env"
$ rustc --version
```

Build and run:
```
$ cd rgen
$ cargo build --release
$ target/release/rgen gen --gen-cores 4
```


## License

MIT. See LICENSE in the top folder.


~~
