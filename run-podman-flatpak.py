#! /usr/bin/python3

def get_aqucire_load_so():
    def get_not_fount_so(bin):
        import subprocess

        reslut = subprocess.run("ldd {bin}".format(bin=bin), shell=True, capture_output=True, text=True)
        if reslut.returncode != 0:
            raise Exception(reslut.stderr)
        
        not_found_so = []
        for line in reslut.stdout.splitlines():
            if not "not found" in line:
                continue

            parts = line.split('=>', maxsplit=2)
            so_name = parts[0].strip()

            not_found_so.append(so_name)

        return not_found_so
    
    def query_so_path(so):
        import os

        return os.path.join('/run/host/lib64', so)
    
    not_found_so = get_not_fount_so('/run/host/bin/podman')
    
    query_pos = 0
    found_so = []
    while len(not_found_so) > query_pos:
        for idx in range(query_pos, len( not_found_so)):
            query_pos = idx+1
            need_query_so = not_found_so[idx]

            real_path = query_so_path(need_query_so)
            found_so.append(real_path)

            new_not_found_so = get_not_fount_so(real_path)
            if len(new_not_found_so) == 0:
                continue

            not_found_so.extend(new_not_found_so)

    return found_so




if __name__ == "__main__":
    import os
    import sys

    podman_path = '/run/host/bin/podman'

    argv = sys.argv.copy()
    argv[0] = podman_path
    if not '--url' in argv:
        argv.insert(1, '--url')
        
        xdg_runtime_dir = '/run/user/1000'
        if not os.environ.get('XDG_RUNTIME_DIR') is None:
            xdg_runtime_dir = os.environ.get('XDG_RUNTIME_DIR') 

        argv.insert(2, 'unix://{path}'.format(path=os.path.join(xdg_runtime_dir, 'podman/podman.sock')))

    env = os.environ.copy()

    need_load_so = get_aqucire_load_so()
    env['LD_PRELOAD'] = ':'.join(need_load_so)
    
    os.execve(podman_path, argv,  env)
    