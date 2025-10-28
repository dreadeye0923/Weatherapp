async function searchWeather() {
    // Step 1: Input ko trim (spaces remove) karo
    const rawCity = document.getElementById('city-search').value.trim();
    
    if (!rawCity) {
        alert("Please enter a city name");
        return;
    }

    // Step 2: City name ko URL ke liye encode karo
    const city = encodeURIComponent(rawCity); 
    
    // Optional: Loading state on karo (agar aapne HTML mein setup kiya hai)
    // showLoading(true);

    try {
        // Fetch call mein encoded 'city' use karo
        const response = await fetch(`http://127.0.0.1:5000/weather?city=${city}`);
        const data = await response.json();

        if (data.error) {
            // Agar OpenWeatherMap ko city nahi mili, toh aapka app.py 404 error dega
            alert(`Error: ${data.error}. Please check the city spelling.`);
            return;
        }

        // Ab yahan apne HTML elements update karo
        document.getElementById('city-name').innerText = data.city;
        
        // Temperature ko round off karna accha lagta hai
        document.getElementById('temperature').innerText = Math.round(data.temperature) + "°C"; 
        document.getElementById('weather-description').innerText = data.description;
        
        document.getElementById('feels-like').innerText = Math.round(data.feels_like) + "°C";
        document.getElementById('humidity').innerText = data.humidity + "%";
        document.getElementById('wind-speed').innerText = data.wind_speed.toFixed(1) + " km/h";

    } catch (error) {
        console.error("Error fetching weather:", error);
        alert("Failed to connect to the weather service.");
    } finally {
        // Optional: Loading state off karo
        // showLoading(false);
    }
}
