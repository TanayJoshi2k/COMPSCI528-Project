# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "E:/EspressIf/ESP-IDF/components/bootloader/subproject"
  "E:/Mobile_Ubiquitous_ESP/UAV-automation/IMU/build/bootloader"
  "E:/Mobile_Ubiquitous_ESP/UAV-automation/IMU/build/bootloader-prefix"
  "E:/Mobile_Ubiquitous_ESP/UAV-automation/IMU/build/bootloader-prefix/tmp"
  "E:/Mobile_Ubiquitous_ESP/UAV-automation/IMU/build/bootloader-prefix/src/bootloader-stamp"
  "E:/Mobile_Ubiquitous_ESP/UAV-automation/IMU/build/bootloader-prefix/src"
  "E:/Mobile_Ubiquitous_ESP/UAV-automation/IMU/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "E:/Mobile_Ubiquitous_ESP/UAV-automation/IMU/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "E:/Mobile_Ubiquitous_ESP/UAV-automation/IMU/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
