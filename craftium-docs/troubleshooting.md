# Troubleshooting

## Problems with the SDL offscreen driver in headless mode

Problems with the SDL offscreen driver are often caused by two reasons:

1. The SDL library installed in the system wasn't built with offscreen driver support.
2. There are multiple versions of SDL and Luanti isn't picking the right one.

### Case 1

This program can be used to list available SDL drivers.

```c
  #include <SDL.h>
  #include <stdio.h>

  int main(int argc, char* argv[]) {
      // Initialize SDL with the video subsystem
      if (SDL_Init(SDL_INIT_VIDEO) != 0) {
          fprintf(stderr, "SDL_Init Error: %s\n", SDL_GetError());
          return 1;
      }

      // Get the number of available video drivers
      int numDrivers = SDL_GetNumVideoDrivers();
      printf("Number of video drivers available: %d\n", numDrivers);

      // List all available video drivers
      for (int i = 0; i < numDrivers; ++i) {
          printf("Video driver #%d: %s\n", i, SDL_GetVideoDriver(i));
      }

      // Clean up and quit SDL
      SDL_Quit();

      return 0;
  }
```

Compile it with:

```bash
  gcc -o list_sdl_video_drivers list_sdl_video_drivers.c `sdl2-config --cflags --libs`
  ./list_sdl_video_drivers
```

If `offscreen` is not listed, then, you might need to compile SDL with `offscreen`
support:

```bash
  wget https://www.libsdl.org/release/SDL2-2.X.X.tar.gz
  tar -xzf SDL2-2.X.X.tar.gz
  cd SDL2-2.X.X

  ./configure --enable-video-dummy --enable-video-offscreen

  make
  sudo make install
```

### Case 2

If the program from **Case 1** lists the offscreen driver and Luanti shows an error message like this one:

```text
ERROR[Main]: Irrlicht: Unable to initialize SDL: offscreen not available
```

It's possible that you have multiple SDL versions installed in your system and that Luanti isn't choosing the right one. If this is the case, you may have to uninstall other SDL versions and keep the one built with the offscreen driver support. See issues [#3](https://github.com/mikelma/craftium/issues/3) and [#11](https://github.com/mikelma/craftium/issues/11) for additional information.

If the issue still persist (😓), consider opening a new [issue in GitHub](https://github.com/mikelma/craftium/issues) detailing the error messages and followed steps.
