import os
import sys
import subprocess
import glob

BASE_SPACE = "/root/src"

class Builder:
    def __init__(self, envs):
        if envs.get('GIT_CLONE_URL'):
            self.git_clone_URL = envs.get('GIT_CLONE_URL').rstrip('/')
            self.git_ref = envs.get('GIT_REF') or 'master'
        elif envs.get('_WORKFLOW_GIT_CLONE_URL'):
            self.git_clone_URL = envs.get('_WORKFLOW_GIT_CLONE_URL').rstrip('/')
            self.git_ref = envs.get('_WORKFLOW_GIT_REF') or 'master'
        else:
            print("environment variable GIT_CLONE_URL is required", file=sys.stderr)
            exit(1)

        self.project_name = os.path.basename(self.git_clone_URL.rstrip('.git'))

        self.files = envs.get('FILES')
        if not self.files:
            self.files = './**/*.py'

    def run(self):
        os.chdir(BASE_SPACE)

        return self.git_pull() and self.git_reset() and self.build()

    def git_pull(self):
        cmd = ['git', 'clone', '--recurse-submodules', self.git_clone_URL, self.project_name]
        print("Run CMD %s" % ' '.join(cmd), file=sys.stdout)
        r = subprocess.run(cmd)

        if (r.returncode == 0):
            return True
        else:
            print("Git clone failed", file=sys.stderr)
            return False

    def git_reset(self):
        cmd = ['git', 'checkout', self.git_ref, '--']
        print("Run CMD %s" % ' '.join(cmd), file=sys.stdout)
        r = subprocess.run(cmd, cwd=os.path.join(BASE_SPACE, self.project_name))

        if (r.returncode == 0):
            return True
        else:
            print("Git checkout failed", file=sys.stderr)
            return False

    def build(self):
        cmd = ['pylint', '-f', 'json', self.files]
        print("Run CMD %s" % (' '.join(cmd)), file=sys.stdout)
        r = subprocess.run(cmd, cwd=os.path.join(BASE_SPACE, self.project_name), stdout=subprocess.PIPE)

        out = str(r.stdout, 'utf-8').strip()
        print(out, file=sys.stdout)

        if (r.returncode != 0):
            return False
        return True

