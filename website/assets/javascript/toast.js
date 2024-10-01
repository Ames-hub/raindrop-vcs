function toast(message, toast_timeout=5000) {
    // Calculate the start time for the fade-out animation
    const fadeOutStart = toast_timeout - 500;

    // Create a style element for the keyframes
    const style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = `
        @keyframes slide-down {
            0% {
                transform: translateX(-50%) translateY(-100%);
            }
            100% {
                transform: translateX(-50%) translateY(25px);
            }
        }
        @keyframes fade-out {
            0% {
                opacity: 1;
            }
            100% {
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Create the toast element
    const toast_div = document.createElement('div');
    toast_div.className = 'toast';
    toast_div.innerHTML = message;

    // Apply styles to the toast element
    toast_div.style.position = 'fixed';
    toast_div.style.background = 'linear-gradient(90deg, #2196F3, #21CBF3)'; // Soft blue gradient
    toast_div.style.color = 'white';
    toast_div.style.padding = '10px';
    toast_div.style.borderRadius = '15px';
    toast_div.style.zIndex = '1000';
    toast_div.style.top = '0';
    toast_div.style.left = '50%';
    toast_div.style.transform = 'translateX(-50%)';
    toast_div.style.width = 'fit-content';
    toast_div.style.maxWidth = '80%';
    toast_div.style.minWidth = '200px';
    toast_div.style.height = 'fit-content';
    toast_div.style.maxHeight = '400px';
    toast_div.style.minHeight = '25px';
    toast_div.style.textAlign = 'center';
    toast_div.style.animation = `slide-down 0.5s ease-in-out, fade-out 0.5s ${fadeOutStart}ms ease-in-out`;

    // Sets border
    toast_div.style.border = '2px solid black';

    // Add text shadow for contrast
    toast_div.style.textShadow = '1px 1px 2px black, 0 0 1em red, 0 0 0.2em red';

    // Append the toast to the body
    document.body.appendChild(toast_div);

    // Ensure the toast stays 50px from the top after the animation ends
    toast_div.addEventListener('animationend', () => {
        toast_div.style.transform = 'translateX(-50%) translateY(25px)';
    });

    // Timeout to remove the toast after the specified time
    setTimeout(() => {
        toast_div.remove();
        // Remove the style element from the head
        style.remove();
    }, toast_timeout);
}