import platform
from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

import numpy


BUILD_ERRORS = (
    CCompilerError,
    DistutilsExecError,
    DistutilsPlatformError,
    OSError,
    ValueError
)


class OptionalBuildExt(build_ext):
    def build_extensions(self):
        compiler_type = self.compiler.compiler_type
        extra_compile_args = []

        if compiler_type == 'unix':
            # Keep preprocessing numerics conservative for this extension only.
            # These flags reduce fused-multiply-add contraction and unsafe
            # reassociation, but they do not make libm transcendental results
            # bit-identical across different operating systems or toolchains.
            extra_compile_args.extend(['-ffp-contract=off', '-fno-fast-math'])

            machine = platform.machine().lower()
            if machine in {'amd64', 'i386', 'i686', 'x86_64'}:
                extra_compile_args.append('-mno-fma')
        elif compiler_type == 'msvc':
            extra_compile_args.append('/fp:strict')

        for extension in self.extensions:
            extension.extra_compile_args = list(extension.extra_compile_args) + extra_compile_args

        try:
            super().build_extensions()
        except BUILD_ERRORS as exc:
            self._warn_optional_failure(exc)

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except BUILD_ERRORS as exc:
            self._warn_optional_failure(exc)

    @staticmethod
    def _warn_optional_failure(exc):
        print(
            "WARNING: building the optional FlowIO preprocessing extension failed; "
            "falling back to the Python/NumPy implementation.\n"
            f"Reason: {exc}"
        )


setup(
    ext_modules=[
        Extension(
            'flowio._preprocessing_ext',
            sources=['src/flowio/_preprocessing_ext.c'],
            include_dirs=[numpy.get_include()],
            define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_19_API_VERSION')],
        )
    ],
    cmdclass={'build_ext': OptionalBuildExt},
)
