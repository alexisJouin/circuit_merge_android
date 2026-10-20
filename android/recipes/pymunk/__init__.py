from pythonforandroid.recipe import CompiledComponentsPythonRecipe

class PymunkRecipe(CompiledComponentsPythonRecipe):
    name = 'pymunk'
    version = '7.3.0'
    url = 'https://files.pythonhosted.org/packages/e3/28/988198dded8d0c9efcd872dd5bafa5e25654f29f500a4601c4c6fcb5b379/pymunk-7.3.0.tar.gz'
    sha256sum = '11de74fdce68f47514c2e6e58ef5502a0bb68ba1c3c77e4e359baa466e9d4c16'
    depends = ['cffi', 'setuptools']
    # setup.py build_ext runs in hostpython and needs CFFI's setuptools hook.
    # The Android CFFI recipe only installs the target build, not this host tool.
    hostpython_prerequisites = ['setuptools', 'cffi==2.0.0']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['LDFLAGS'] += ' -llog -lm -Wl,-z,max-page-size=16384'
        return env

recipe = PymunkRecipe()
