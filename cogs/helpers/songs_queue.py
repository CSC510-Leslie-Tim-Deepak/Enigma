"""
This file is responsible for maintaining the song queue
"""
from random import shuffle
from yt_dlp import YoutubeDL
# Make a singleton class for the song queue


class Singleton(type):
    """A metaclass that creates a Singleton base type when called."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Create a new instance of the class if it does not exist."""
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Songs_Queue(metaclass=Singleton):
    """
    This class is responsible for maintaining the song queue. There will only be one instance of this class
    """

    def __init__(self):
        """Get the instance of Songs_Queue, or create a new one if there is no instance. 
        A new instance will have an empty queue so songs must be added using the add_to_queue method.
        """
        self._queue = []
        self._index = 0
        self._dislikes = {}  # Tracks dislikes for songs: {song_name: dislike_count}


    @property
    def queue(self):
        """Return the current queue."""
        return self._queue

    @property
    def index(self):
        """Return the current index."""
        return self._index

    async def handle_empty_queue(self, ctx):
        """
        Helper function to handle empty song queue
        """

        if self.get_len() == 0:
            await ctx.send(
                "No recommendations present. First generate recommendations using !poll or !mood."
            )
            return True
        return False

    def clear(self):
        """Clear the current queue."""
        self._queue.clear()
        self._index = 0

    def get_song_at_index(self, idx):
        """
        This function returns the song at the given index in the queue. Returns the song as a string in format "<Song Name> by <Artist Name>"

        Parameters:
            idx(int): The index of the song in the queue

        Returns:
            str: The song at the given index in the queue, or -1 if the index is out of bounds
        """
        
        if idx < 0 or idx >= len(self.queue):
            return -1
        song = self.queue[idx]
        artist = song[1]
        if artist == "Unknown":
            return song[0]
        return f"{song[0]} by {song[1]}"

    def current_song(self):
        """Return the current song."""
        return self.get_song_at_index(self._index)
    
    def next_song(self):
        """
        This function returns the next song in the queue
        """
        
        
        if (self._index == len(self.queue) - 1):
            self._index = 0
        else:
            self._index += 1
        val = self._index
        return self.get_song_at_index(val)

    def prev_song(self):
        """
        This function returns the previous song in the queue
        """

        self._index -= 1
        if (self._index < 0):
            self._index = len(self.queue) - 1
        val = self._index
        return self.get_song_at_index(val)
    
    def current_idx(self):
        """Return the current index"""
        return self._index
    
    def next_idx(self):
        """Return the index of the next song"""
        if (self._index == len(self.queue) - 1):
            self._index = 0
        else:
            self._index += 1
        return self._index
    
    def prev_idx(self):
        """
        This function returns the index of the previous song in the queue
        """

        self._index -= 1
        if (self._index < 0):
            self._index = len(self.queue) - 1
        return self._index

    def move_song(self, song_name, idx):
        """
        This function moves a song within the queue
        """

        curr_idx = -1
        if int(idx) < 1 or int(idx) > len(self.queue) - 1:
            return -2
        for index, s in enumerate(self.queue):
            title = s[0]
            if title.upper() == song_name.upper():
                curr_idx = index
        if curr_idx != -1:
            # Remove the element from the old index
            element = self.queue.pop(curr_idx)
            # Insert the element at the new index
            self.queue.insert(int(idx), element)
            return int(idx)
        else:
            return -1

    def get_len(self):
        """
        This function returns the length of the song queue
        """

        return len(self.queue)

    def return_queue(self):
        """
        This function returns song queue and the current index of the song that is playing
        """

        return (self.queue, self._index)

    def shuffle_queue(self):
        """
        This function shuffles the song queue
        """
        element = self.queue.pop(self._index)
        shuffle(self.queue)
        self.queue.insert(self._index, element)

    def add_to_queue(self, songs: list[str]):
        """
        This function adds a song to the queue

        Parameters:
            song_name(str | list[str]): The name of the song to be added to the queue, or a list of song names to be added to the queue
        """

        def is_url(input_str):
            if isinstance(input_str, tuple):
                return False
            return input_str.startswith("http://") or input_str.startswith("https://")
        for song in songs:
            if is_url(song):
                site_name = "Direct URL"
                search_prefix = "None"
                song_name = song
                artist = "Unknown"
            else:
                if isinstance(song, tuple):
                    song_name = " ".join(song[0].split()[1:])
                    artist = song[1]

                    if song[0].split(" ", 1)[0] == "yt":
                        site_name = "YouTube"
                        search_prefix = 'ytsearch'    
                    elif song[0].split(" ", 1)[0] == "sc":  # Prefix-based SoundCloud searc
                        site_name = "SoundCloud"
                        search_prefix = "scsearch"
                    else:
                        print("Specify a platform for searching! Use `yt` for YouTube or `sc` for SoundCloud.")
                        return
                else:
                    song_name = " ".join(song.split()[1:])
                    artist = "Unknown"
                    if song.split(" ", 1)[0] == "yt":
                        site_name = "YouTube"
                        search_prefix = 'ytsearch'
                    elif song.split(" ", 1)[0] == "sc":  # Prefix-based SoundCloud searc
                        site_name = "SoundCloud"
                        search_prefix = "scsearch"
                    else:
                        print("Specify a platform for searching! Use `yt` for YouTube or `sc` for SoundCloud.")
                        return
            """
            ydl_opts = {
                'format': 'bestaudio',
                'noplaylist': True,
                'quiet': True,  # Suppress verbose output
                'source_address': '0.0.0.0',  # Prevent IPv6 issues
            }   
            ydl_opts['default_search'] = search_prefix

            with YoutubeDL(ydl_opts) as ydl:
                try:
                    # Extract info from the URL or perform the search
                    query = f"{song_name} {artist}" if artist != "Unknown" else song_name

                    info = ydl.extract_info(query, download=False)
                    if 'entries' in info:
                        info = info['entries'][0]  # Get the first result from the search
                    url = info['url']
                    title = info.get('title', 'Unknown Title') + " from " + site_name
                except Exception as e:
                    print(f"An error occurred: {e}")
                    return
            """
            title = ""
            self.queue.append((song_name, artist, site_name, search_prefix, title))

    def remove_from_queue(self, song_name):
        """
        This function removes a song from the queue

        Parameters:
            song_name(str): The name of the song to be removed from the queue

        Returns:
            int: The index of the song that was removed from the queue, or -1 if the song was not found in the queue
        """

        for index, song in enumerate(self.queue):
            title = song[0]
            artist = song[1]
            if title.upper() == song_name.upper():
                if index != self.index:
                    return self.queue.pop(index)
                elif index == 0:
                    # If the song to be removed is the first song in the queue
                    self.queue.pop(index)
                    if (self._index == len(self.queue)):
                        self._index = 0
                    return index
                else:
                    self.queue.pop(index)
                    self._index -= 1
                    if (self._index < 0):
                        self._index = len(self.queue) - 1
                    return index
                
    ## ADD dislike feature
    def add_dislike(self, song_name):
        """
        Increment dislike count for the given song.
        """
        if song_name not in self._dislikes:
            self._dislikes[song_name] = 1
        else:
            self._dislikes[song_name] += 1

    def get_dislikes(self, song_name):
        """
        Get the dislike count for a song.
        """
        return self._dislikes.get(song_name, 0)

    def reset_dislikes(self, song_name):
        """
        Reset dislikes for a song when skipped or removed.
        """
        if song_name in self._dislikes:
            del self._dislikes[song_name]

        return -1
