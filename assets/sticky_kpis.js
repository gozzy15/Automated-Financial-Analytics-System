window.addEventListener("scroll", function () {

    const sticky = document.getElementById("sticky-kpi-container");

    if (!sticky) return;

    if (window.scrollY > 15) {

        sticky.classList.add("kpi-shrink");

    } else {

        sticky.classList.remove("kpi-shrink");

    }

});