Promise.all(Array.from(document.images).filter(img => !img.complete).map(img => new Promise(resolve => { img.onload = img.onerror = resolve; }))).then(() => {
    console.log('images finished loading');
    images = document.getElementsByTagName("img");
    for (image of images) {
        image.src = image.getAttribute("src");
    }
});
