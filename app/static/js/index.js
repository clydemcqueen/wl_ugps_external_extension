let el_ext = document.getElementById("extension_status");
let el_gga = document.getElementById("gga_status");
let el_hdt = document.getElementById("hdt_status");
let el_inject = document.getElementById("inject_status");
let el_nmea = document.getElementById("nmea_status");
let el_g2_acoustic = document.getElementById("g2_acoustic_status");
let el_g2_position = document.getElementById("g2_position_status");
let el_g2_orientation = document.getElementById("g2_orientation_status");

function showStatus(el, status, good_text, bad_text) {
    if (status) {
        el.textContent = good_text;
        el.className = "status_good";
    } else {
        el.textContent = bad_text;
        el.className = "status_bad"
    }
}

function showNmeaStatus(status) {
    if (status === 'disabled') {
        el_nmea.textContent = 'NMEA logging disabled';
        el_nmea.className = 'status_unknown';
    } else if (status === 'waiting') {
        el_nmea.textContent = 'NMEA logging enabled, waiting for messages';
        el_nmea.className = 'status_waiting';
    } else if (status === 'logging') {
        el_nmea.textContent = 'Logging NMEA messages';
        el_nmea.className = 'status_good';
    }
}

function showG2Status(el, status) {
    // There are four states: disabled, waiting, failed, success
    if (status.status === 'DISABLED') {
        el.textContent = status.name + ' logging disabled';
        el.className = 'status_unknown';
    } else if (status.status === 'WAITING') {
        el.textContent = status.name + ' logging enabled';
        el.className = 'status_waiting';
    } else if (status.status === 'FAILED') {
        el.textContent = status.name + ' polling failed; is the bridge up?';
        el.className = 'status_bad';
    } else if (status.status === 'SUCCESS') {
        let text = status.name + ': ';
        if (status.name === 'Acoustic') {
            text += status.data.receiver_distance[0].toFixed(2) + ', ' +
                status.data.receiver_distance[1].toFixed(2) + ', ' +
                status.data.receiver_distance[2].toFixed(2) + ', ' +
                status.data.receiver_distance[3].toFixed(2);
        } else if (status.name === 'Vessel position') {
            text += status.data.lat.toFixed(4) + ', ' +
                status.data.lon.toFixed(4) + ', ' +
                status.data.orientation.toFixed(1);
        } else if (status.name === 'Vessel orientation') {
            text += status.data.roll.toFixed(1) + ', ' +
                status.data.pitch.toFixed(1) + ', ' +
                status.data.yaw.toFixed(1);
        }
        el.textContent = text;
        el.className = 'status_good';
    }
}

async function getStatus() {
    try {
        const response = await fetch("/status");
        if (response.ok) {
            el_ext.textContent = "Listening on 192.168.2.2:6200";
            el_ext.className = "status_good";

            const {gga_status, hdt_status, inject_status, latitude, longitude, heading, ugps_host, send_rate, nmea_logging_status, g2_logging_status} = await response.json();

            showStatus(el_gga, gga_status,
                " Receiving GGA: " + latitude.toFixed(4).toString() + ", " + longitude.toFixed(4).toString(),
                "Waiting for GGA");

            showStatus(el_hdt, hdt_status,
                "Receiving HDT: " + heading.toFixed(1).toString(),
                "Waiting for HDT");

            showStatus(el_inject, inject_status,
                "Sending to " + ugps_host + " at " + send_rate + "Hz",
                "Not sending to " + ugps_host + " at " + send_rate + "Hz");

            showNmeaStatus(nmea_logging_status);

            showG2Status(el_g2_acoustic, g2_logging_status[0]);
            showG2Status(el_g2_position, g2_logging_status[1]);
            showG2Status(el_g2_orientation, g2_logging_status[2]);

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

    el_nmea.textContent = "NMEA logging status unknown";
    el_nmea.className = "status_unknown";

    el_g2_acoustic.textContent = "Acoustic logging status unknown";
    el_g2_acoustic.className = "status_unknown";

    el_g2_position.textContent = "Vessel position logging status unknown";
    el_g2_position.className = "status_unknown";

    el_g2_orientation.textContent = "Vessel orientation logging status unknown";
    el_g2_orientation.className = "status_unknown";
}

setInterval(getStatus, 500);
