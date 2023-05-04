from wasmtime import Config, Engine, Linker, Module, Store, WasiConfig

def main():
    cfg = Config()

    # necessary if we want to interrupt execution after some amount of instructions executed
    cfg.consume_fuel = True 
    cfg.cache = True

    engine = Engine(cfg)

    linker = Linker(engine)
    linker.define_wasi()
    
    """
    from https://wasmlabs.dev/articles/python-wasm32-wasi/
    wget https://github.com/vmware-labs/webassembly-language-runtimes/releases/download/python%2F3.11.1%2B20230118-f23f3f3/python-aio-3.11.1.zip
    unzip python-aio-3.11.1.zip
    rm python-aio-3.11.1.zip
    tree
    .
    ├── app.py [new]
    ├── bin
    │   ├── python-3.11.1-wasmedge.wasm
    │   └── python-3.11.1.wasm
    ├── runner.py [this file]
    └── usr
        └── local
            └── lib
                ├── python3.11
                │   ├── lib-dynload
                │   └── os.py
                └── python311.zip
    """

    module = Module.from_file(linker.engine, "python/python-3.11.3/bin/python-3.11.3.wasm")

    config = WasiConfig()
    config.argv = ("python", "untrusted_code/sample.py")

    config.preopen_dir("./python/python-3.11.3", "/")
    config.preopen_dir("./untrusted_code", "/untrusted_code")
    
    # mkdir chroot, which is an arbitrary name for a directory
    config.stdout_file = 'logs/out.log' # will be created if it doesn't exist
    config.stderr_file = 'logs/err.log' # will be created if it doesn't exist

    store = Store(linker.engine)
    
    store.add_fuel(500_000_000) # amount of fuel limits how many instructions can be executed
    store.set_wasi(config)
    instance = linker.instantiate(store, module)

    # _start is the default wasi main function
    start = instance.exports(store)["_start"]
    
    mem = instance.exports(store)["memory"]
    mem_size = mem.size(store)
    data_len = mem.data_len(store)

    print(f"mem.size: {mem_size} pages of 64kb")
    print(f"mem.data_len: {data_len:_}")
    
    start(store)
    consumed = store.fuel_consumed()
    print(f"fuel consumed: {consumed:_}")

    with open('logs/out.log') as f:
        print(f.read())

if __name__ == '__main__':
    main()
