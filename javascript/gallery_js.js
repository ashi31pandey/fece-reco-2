document.addEventListener("DOMContentLoaded", function() {
    const showPhotosButton = document.getElementById('showPhotos');
    const showVideosButton = document.getElementById('showVideos');
    const photosSection = document.getElementById('photos');
    const videosSection = document.getElementById('videos');

    showPhotosButton.addEventListener('click', function() {
        photosSection.classList.remove('hidden');
        videosSection.classList.add('hidden');
    });

    showVideosButton.addEventListener('click', function() {
        videosSection.classList.remove('hidden');
        photosSection.classList.add('hidden');
    });
});
