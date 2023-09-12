let el_ext = document.getElementById("extension_status");
let el_gga = document.getElementById("gga_status");
let el_hdt = document.getElementById("hdt_status");
let el_inject = document.getElementById("inject_status");

function showStatus(el, status, good_text, bad_text) {
    if (status) {
        el.textContent = good_text;
        el.className = "status_good";
    } else {
        el.textContent = bad_text;
        el.className = "status_bad"
    }
}

async function getStatus() {
    try {
        const response = await fetch("/status");
        if (response.ok) {
            el_ext.textContent = "Listening on 192.168.2.2:6200";
            el_ext.className = "status_good";

            const {gga_status, hdt_status, inject_status, latitude, longitude, heading, ugps_host, send_rate} = await response.json();

            showStatus(el_gga, gga_status,
                " Receiving GGA: " + latitude.toFixed(4).toString() + ", " + longitude.toFixed(4).toString(),
                "Waiting for GGA");

            showStatus(el_hdt, hdt_status,
                "Receiving HDT: " + heading.toFixed(1).toString(),
                "Waiting for HDT");

            showStatus(el_inject, inject_status,
                "Sending to " + ugps_host + " at " + send_rate + "Hz",
                "Not sending to " + ugps_host + " at " + send_rate + "Hz");

            return;
        }
    } catch {
        // Catch all network errors
    }

    el_ext.textContent = "Extension not responding";
    el_ext.className = "status_bad";

    el_gga.textContent = "GGA status unknown";
    el_gga.className = "status_unknown";

    el_hdt.textContent = "HDT status unknown";
    el_hdt.className = "status_unknown";

    el_inject.textContent = "Injection status unknown";
    el_inject.className = "status_unknown";
}

setInterval(getStatus, 500);
