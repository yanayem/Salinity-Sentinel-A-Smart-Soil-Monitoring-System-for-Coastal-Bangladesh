window.onload = function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((pos) => {
            document.getElementById('latitude').value = pos.coords.latitude;
            document.getElementById('longitude').value = pos.coords.longitude;
        });
    }

    // Dynamic background based on temperature
    const tempCard = document.querySelector('.current-weather');
    if(tempCard){
        const tempText = tempCard.textContent.match(/(-?\d+)/);
        if(tempText){
            const temp = parseInt(tempText[0]);
            if(temp >= 30){
                document.body.style.background = 'linear-gradient(135deg, #FF5733, #FFC300)';
            } else if(temp >= 15){
                document.body.style.background = 'linear-gradient(135deg, #3498DB, #2ECC71)';
            } else{
                document.body.style.background = 'linear-gradient(135deg, #2C3E50, #34495E)';
            }
        }
    }
}
