import streamlit.components.v1 as components


def display_live_clock():
    """
    Display a live market clock showing:

    • US Eastern Time (ET)
    • Local Time (automatically detected)

    The clocks update every second without rerunning
    the Streamlit application.
    """

    html = """
    <div style="
        background:#c1c1c1;
        border:1px solid #E5E7EB;
        border-radius:10px;
        padding:15px;
        margin-bottom:18px;
        font-family:Arial, Helvetica, sans-serif;
    ">

        <div style="
            font-size:18px;
            font-weight:700;
            margin-bottom:15px;
        ">
            🕒 Current Market Time
        </div>

        <div style="margin-bottom:14px;">

            <div style="
                color:#2563EB;
                font-size:15px;
                font-weight:600;
            ">
                🇺🇸 Eastern Time (ET)
            </div>

            <div
                id="et_clock"
                style="
                    font-size:20px;
                    font-weight:700;
                    margin-top:4px;
                ">
            </div>

        </div>

        <div>

            <div
                id="local_label"
                style="
                    color:#059669;
                    font-size:15px;
                    font-weight:600;
                ">
                🌍 Local Time
            </div>

            <div
                id="local_clock"
                style="
                    font-size:20px;
                    font-weight:700;
                    margin-top:4px;
                ">
            </div>

        </div>

    </div>

<script>

function formatClock(date, timezone){

    const options = {

        weekday:'short',
        month:'short',
        day:'2-digit',

        hour:'2-digit',
        minute:'2-digit',
        second:'2-digit',

        hour12:true,

        timeZone:timezone

    };

    const parts =
        new Intl.DateTimeFormat(
            'en-US',
            options
        ).formatToParts(date);

    let values = {};

    parts.forEach(function(part){

        values[part.type] = part.value;

    });

    return (
        values.weekday +
        " " +
        values.month +
        " " +
        values.day +
        " • " +
        values.hour +
        ":" +
        values.minute +
        ":" +
        values.second +
        " " +
        values.dayPeriod
    );

}

function updateClock(){

    const now = new Date();

    document.getElementById("et_clock").innerHTML =
        formatClock(
            now,
            "America/New_York"
        );

    const localZone =
        Intl.DateTimeFormat().resolvedOptions().timeZone;

    const timezoneName =
        now.toLocaleTimeString(
            "en-US",
            {
                timeZoneName: "short"
            }
        ).split(" ").pop();

    document.getElementById("local_label").innerHTML =
        "🌍 Local Time (" + timezoneName + ")";

    document.getElementById("local_clock").innerHTML =
        formatClock(
            now,
            localZone
        );

}

updateClock();

setInterval(updateClock,1000);

</script>
"""

    components.html(
        html,
        height=180,
    )