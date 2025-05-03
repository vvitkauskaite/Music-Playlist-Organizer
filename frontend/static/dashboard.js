$(document).ready(function () {
  let currentAudio = null;
  let currentSongTitle = "";
  const progressBar = $("#progress-bar");
  let currentPlaylistName = "";

  loadSongs();
  loadPublicSongs();
  loadPlaylists();
  fetchHistory(); // Load history on page load

  $("#upload-form").submit(function (e) {
    e.preventDefault();
    const file = $("#upload-song")[0].files[0];
    if (!file) return alert("Select a file");
    const formData = new FormData();
    formData.append("file", file);
    $.ajax({
      url: "/upload_song",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: () => {
        $("#upload-song").val("");
        loadSongs();
      }
    });
  });

  $("#create-playlist-form").submit(function (e) {
    e.preventDefault();
    const name = $("#playlist-name").val().trim();
    if (!name) return;
    $.ajax({
      url: "/create_playlist",
      type: "POST",
      data: JSON.stringify({ name }),
      contentType: "application/json",
      dataType: "json",
      success: () => {
        $("#playlist-name").val("");
        loadPlaylists();
      },
      error: (xhr) => {
        alert(xhr.responseJSON?.message || "Failed to create playlist");
      }
    });
  });

  function fetchHistory() {
    $.ajax({
      url: "/history",
      type: "GET",
      dataType: "json",
      success: function (data) {
        if (data && data.history && data.history.length > 0) {
          $("#history-output").html(data.history[0]);
        } else {
          $("#history-output").html("<i>No history available</i>");
        }
      },
      error: function () {
        $("#history-output").html("<i>Failed to load history</i>");
      }
    });
  }

  function playSong(src, title, isPublic) {
  if (currentAudio) {
    currentAudio.pause();
    if (currentSongTitle === title) {
      currentSongTitle = "";
      $("#play-pause-btn").text("▶️ Play");
      return;
    }
  }

  currentAudio = new Audio(src);
  currentAudio.volume = $("#volume-slider").val() / 100;
  currentAudio.loop = false;
  currentAudio.play();
  currentSongTitle = title;
  $("#current-song").text(title.replace(/\.mp3$/i, ""));
  progressBar.val(0);
  $("#play-pause-btn").text("⏸️ Pause");

  currentAudio.addEventListener("timeupdate", () => {
    progressBar.attr("max", currentAudio.duration);
    progressBar.val(currentAudio.currentTime);
  });

  currentAudio.addEventListener("ended", () => {
    playNextSong();
  });

  // ⬇️ Naudojame fetch su credentials
  fetch("/play_song", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename: title, is_public: isPublic }),
    credentials: "include" // 🔥 labai svarbu!
  })
    .then(response => response.json())
    .then(() => setTimeout(fetchHistory, 300))
    .catch(err => console.error("Failed to log play:", err));


  }

  function playNextSong() {
    const allButtons = $(".play-button");
    let found = false;

    allButtons.each(function () {
      const thisTitle = $(this).data("title");
      if (found) {
        $(this).click(); // play the next one
        return false;
      }
      if (thisTitle === currentSongTitle) {
        found = true;
      }
    });

    if (!found || allButtons.length === 1) {
      currentSongTitle = "";
      $("#current-song").text("No more songs");
      $("#play-pause-btn").text("▶️ Play");
    }
  }

  function makeDraggable(li, filename, isPublic) {
    li.attr("draggable", "true").on("dragstart", function (e) {
      e.originalEvent.dataTransfer.setData("text/plain", JSON.stringify({
        title: filename,
        public: isPublic
      }));
    });
  }

  function loadSongs() {
    $.get("/songs", function (data) {
      const list = $("#song-list").empty();
      data.songs.forEach(song => {
        const name = song.filename.replace(/\.mp3$/i, "");
        const li = $(`<li><span>🎵 ${name}</span><button class='play-button' data-src='${song.url}' data-title='${song.filename}' data-public='false'>▶️</button></li>`);
        li.find(".play-button").click(function () {
          playSong($(this).data("src"), $(this).data("title"), false);
        });
        makeDraggable(li, song.filename, false);
        list.append(li);
      });
    });
  }

  function loadPublicSongs() {
    $.get("/public_songs", function (data) {
      const list = $("#public-song-list").empty();
      data.songs.forEach(song => {
        const name = song.filename.replace(/\.mp3$/i, "");
        const li = $(`<li><span>🌐 ${name}</span><button class='play-button' data-src='${song.url}' data-title='${song.filename}' data-public='true'>▶️</button></li>`);
        li.find(".play-button").click(function () {
          playSong($(this).data("src"), $(this).data("title"), true);
        });
        makeDraggable(li, song.filename, true);
        list.append(li);
      });
    });
  }

  function loadPlaylists(callback) {
    $.get("/playlists", function (data) {
      const list = $("#playlist-list").empty();
      data.playlists.forEach(pl => {
        const li = $(`<li class='playlist-item'>📁 ${pl.name}</li>`);
        li.click(() => showPlaylistPopup(pl.name));
        list.append(li);
      });
      if (callback) callback();
    });
  }

  function showPlaylistPopup(playlistName) {
    currentPlaylistName = playlistName;
    $.get("/playlists", function (data) {
      const playlist = data.playlists.find(p => p.name === playlistName);
      if (!playlist) return;

      $("#popup-title").text(playlist.name);
      const descText = playlist.description?.trim();
      const descElem = $("#popup-description");
      if (descText) {
        descElem.text(descText).removeClass("placeholder");
      } else {
        descElem.text("add description").addClass("placeholder");
      }

      $("#playlist-img").attr("src", `/static/${playlist.picture || "default_picture.png"}`);
      const list = $("#popup-song-list").empty();
      playlist.songs.forEach((s, i) => {
        const name = s.replace(/\.mp3$/, "");
        list.append(`
          <li>
            ${i + 1}. ${name}
            <button onclick='playSongFromPlaylist("${s}.mp3")'>▶️</button>
            <button onclick='removeSongFromPlaylist("${s}")'>➖</button>
          </li>
        `);
      });
      $("#playlist-popup").fadeIn();
    });
  }

  window.removeSongFromPlaylist = function (filename) {
    $.ajax({
      url: "/playlist/remove_song",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        playlist: currentPlaylistName,
        song: filename,
        is_public: filename.includes("🌐")
      }),
      success: () => showPlaylistPopup(currentPlaylistName),
      error: (xhr) => alert(xhr.responseJSON?.message || "Failed to remove song from playlist")
    });
  };

  $("#popup-description").on("focus", function () {
    if ($(this).text().trim() === "add description") {
      $(this).text("").removeClass("placeholder");
    }
  }).on("blur", function () {
    const text = $(this).text().trim();
    if (!text) {
      $(this).text("add description").addClass("placeholder");
    } else {
      $(this).removeClass("placeholder");
    }
  });

  $("#playlist-song-search").on("input", function () {
    const query = $(this).val().toLowerCase();
    const resultsList = $("#popup-song-search-results").empty();
    if (!query) return;

    $.when($.get("/songs"), $.get("/public_songs")).done((localData, publicData) => {
      const allSongs = [
        ...localData[0].songs.map(s => ({ ...s, isPublic: false })),
        ...publicData[0].songs.map(s => ({ ...s, isPublic: true }))
      ];

      const matches = allSongs.filter(song => song.filename.toLowerCase().includes(query));
      if (matches.length === 0) {
        resultsList.append(`<li style="font-style: italic;">No songs found.</li>`);
        return;
      }

      matches.slice(0, 3).forEach(song => {
        const name = song.filename.replace(/\.mp3$/i, "");
        const li = $(`<li>${song.isPublic ? "🌐" : "🎵"} ${name}<button class="add-song-btn">➕</button></li>`);
        li.find(".add-song-btn").click(() => {
          $.ajax({
            url: "/playlist/add_song",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({
              playlist: currentPlaylistName,
              song: song.filename,
              is_public: song.isPublic
            }),
            success: () => {
              showPlaylistPopup(currentPlaylistName);
              resultsList.empty();
              $("#playlist-song-search").val("");
            },
            error: (xhr) => {
              alert(xhr.responseJSON?.message || "Failed to add song to playlist");
            }
          });
        });
        resultsList.append(li);
      });
    });
  });

  window.playSongFromPlaylist = function (title) {
    const match = $(`.play-button[data-title='${title}']`);
    if (match.length > 0) match[0].click();
    else alert("Song not found in library.");
  };

  $("#close-popup").click(() => $("#playlist-popup").fadeOut());

  $("#playlist-img").click(function () {
    $('<input type="file" accept="image/*">').on("change", function () {
      const file = this.files[0];
      if (!file) return;
      const form = new FormData();
      form.append("image", file);
      form.append("playlist", currentPlaylistName);
      $.ajax({
        url: "/playlist/update_image",
        type: "POST",
        data: form,
        contentType: false,
        processData: false,
        success: () => loadPlaylists()
      });
    }).click();
  });

  $("#playlist-popup").on("dragover", e => e.preventDefault());
  $("#playlist-popup").on("drop", function (e) {
    e.preventDefault();
    const data = JSON.parse(e.originalEvent.dataTransfer.getData("text/plain"));
    $.post("/playlist/add_song", JSON.stringify({ playlist: currentPlaylistName, song: data.title, is_public: data.public }), () => loadPlaylists(() => showPlaylistPopup(currentPlaylistName)), "json");
  });

  $("#song-filter").on("input", function () {
    const f = $(this).val().toLowerCase();
    $("#song-list li").each(function () {
      $(this).toggle($(this).text().toLowerCase().includes(f));
    });
  });

  $(document).on("input", "#public-search", function () {
    const f = $(this).val().toLowerCase();
    $("#public-song-list li").each(function () {
      $(this).toggle($(this).text().toLowerCase().includes(f));
    });
  });

  $("#play-pause-btn").click(function () {
    if (currentAudio) {
      if (currentAudio.paused) {
        currentAudio.play();
        $(this).text("⏸️ Pause");
      } else {
        currentAudio.pause();
        $(this).text("▶️ Play");
      }
    }
  });

  $("#loop-btn").click(function () {
    if (currentAudio) {
      currentAudio.loop = !currentAudio.loop;
      alert("Loop is now " + (currentAudio.loop ? "ON" : "OFF"));
    }
  });

  $("#volume-slider").on("input", function () {
    const v = $(this).val();
    $("#volume-label").text(`🔊 ${v}`);
    if (currentAudio) currentAudio.volume = v / 100;
  });

  progressBar.on("input", function () {
    if (currentAudio) currentAudio.currentTime = progressBar.val();
  });

  window.fetchHistory = function () {
    $.get("/history", function (data) {
      if (data && data.history && data.history.length > 0) {
        $("#history-output").html(data.history[0]);
      } else {
        $("#history-output").html("<i>No history found.</i>");
      }
    });
  };

  window.clearHistory = function () {
    $.post("/clear_history", function (data) {
      alert(data.message);
      $("#history-output").text("");
    });
  };

  window.openDeleteModal = function () {
    $("#delete-modal").css({ display: "flex", justifyContent: "center", alignItems: "center" });
  };

  window.closeDeleteModal = function () {
    $("#delete-modal").hide();
  };

  window.confirmDelete = function () {
    $.post("/delete_account", function (res) {
      alert(res.message);
      location.href = "/";
    });
  };
});
