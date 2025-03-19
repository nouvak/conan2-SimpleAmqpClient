from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, replace_in_file, rm, apply_conandata_patches
from conan.tools.scm import Version
import os

class SimpleAmqpClientConan(ConanFile):
    name = "simpleamqpclient"
    version = "2.4.0"
    license = "MIT"
    description = "SimpleAmqpClient is an easy-to-use C++ wrapper around the rabbitmq-c C library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    requires = ["rabbitmq-c/0.9.0", "boost/[>=1.66.0]"]
    exports_sources = "CMakeLists.txt", "Modules/*"

    @property
    def src_dir(self):
        return "%s-%s" % (self.name, self.version)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.shared
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("shared"):
            self.options["boost"].fPIC = True
        self.options["rabbitmq-c"].shared= self.options.get_safe("shared", False) # add rabbitmq-c shared option
        self.options["rabbitmq-c"].ssl = True # add rabbitmq-c ssl option

    def source(self):
        get(self, "https://codeload.github.com/alanxz/SimpleAmqpClient/zip/v%s" % self.version,
            sha1="931e2aa78fc011f8d1ea312541df75b1d5edd559",
            destination=self.src_dir, strip_root=True)
        cmakelist_tst = os.path.join(self.src_dir, "CMakeLists.txt")
        os.unlink("%s/Modules/FindRabbitmqc.cmake" % self.src_dir)
        replace_in_file(self, cmakelist_tst, "SET(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/Modules)", "list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/Modules)")
        replace_in_file(self, cmakelist_tst, "${Rabbitmqc_SSL_ENABLED}", "ON")
        replace_in_file(self, cmakelist_tst, "Rabbitmqc_LIBRARY", "rabbitmq-c_LIBRARIES")
        replace_in_file(self, cmakelist_tst, "Rabbitmqc", "rabbitmq-c")
        #replace_in_file(self, cmakelist_tst, "Boost", "boost")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_INSTALL_PREFIX"] = "install"
        if self.settings.os == "Windows":
            tc.variables["BUILD_SHARED_LIBS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.src_dir)
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, pattern="*.h", src=os.path.join(self.package_folder, "install"), dst=os.path.join(self.package_folder, "include"))
        copy(self, pattern="*.lib", src=os.path.join(self.package_folder, "install"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.dll", src=os.path.join(self.package_folder, "install"), dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, pattern="*.pdb", src=os.path.join(self.package_folder, "install"), dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, pattern="*.so*", src=os.path.join(self.package_folder, "install"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.dylib", src=os.path.join(self.package_folder, "install"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.a", src=os.path.join(self.package_folder, "install"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        # remove empty folders
        rm(self, pattern="install", folder=self.package_folder, recursive=True)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["SimpleAmqpClient.2"]
        else:
            self.cpp_info.libs = ["SimpleAmqpClient"]