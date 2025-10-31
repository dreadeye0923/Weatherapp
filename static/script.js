async function searchWeather(isRefresh = false) {
    // Refresh par, hum current city name use karenge
    const cityInput = document.getElementById('city-search');
    const cityToSearch = isRefresh 
        ? document.getElementById('city-name').textContent 
        : cityInput.value.trim();
    
    if (!cityToSearch || cityToSearch === "Error" || cityToSearch === "Loading...") {
        // Assume you have a showStatus helper function
        if (!isRefresh) showStatus('Please enter a valid city name', 'error'); 
        return;
    }

    // Optional: Loading state on karo
    // if (typeof showLoading === 'function') showLoading(true);

    const encodedCity = encodeURIComponent(cityToSearch); 

    try {
        // Note: Agar aap Ngrok pe the, toh URL ko sirf `/weather...` rakhein. Local host pe dono chalega.
        const response = await fetch(`/weather?city=${encodedCity}`); 
        const data = await response.json();

        // Agar data.error hai ya data.current missing hai, toh error dikhao
        if (data.error || !data.current) {
            // Assume you have a showStatus helper function
            showStatus(`Error: ${data.error || 'Data structure missing.'}`, 'error'); 
            return;
        }
        
        // 🚨 CRITICAL FIX: Data ko data.current se access karo
        const current = data.current; 

        // Ab yahan apne HTML elements update karo
        document.getElementById('city-name').innerText = current.city;
        
        // Temperature, Feels Like, etc. ko current object se access karo
        document.getElementById('temperature').innerText = current.temperature + "°C"; 
        document.getElementById('weather-description').innerText = current.description;
        
        document.getElementById('feels-like').innerText = current.feels_like + "°C";
        document.getElementById('humidity').innerText = current.humidity + "%";
        document.getElementById('wind-speed').innerText = current.wind_speed.toFixed(1) + " km/h";
        
        // 5-Day Forecast update function call karo
        // (Assuming updateForecastDisplay function is defined elsewhere)
        if (typeof updateForecastDisplay === 'function') {
            updateForecastDisplay(data.forecast);
        }

        // Search successful hone par status message
        // if (typeof showStatus === 'function') showStatus(`Weather updated for ${current.city}`, 'success');

    } catch (error) {
        console.error("Error fetching weather:", error);
        // if (typeof showStatus === 'function') showStatus("Failed to connect to the server.", 'error');
    } finally {
        // Optional: Loading state off karo
        // if (typeof showLoading === 'function') showLoading(false);
    }
}