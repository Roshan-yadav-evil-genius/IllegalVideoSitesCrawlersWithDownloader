console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");
console.log("ok");

function tryPlayVideo() {
    const video = document.querySelector('video'); // Assuming there is a single video element

    // Check if the video element exists and if it's paused, then attempt to play
    if (video) {
        video.play();
        const newDiv = document.createElement('div');
        newDiv.id = 'done'; // Set the ID of the new <div> to "donre"
        document.body.appendChild(newDiv);
    }else{
        setTimeout(tryPlayVideo,1000)
    }
}

document.addEventListener('DOMContentLoaded', tryPlayVideo);


