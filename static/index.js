"use strict"

const btnCloseOutline= document.getElementById("close");
const btnMenuOutline = document.getElementById("outline");
const navMenu = document.querySelector(".sideNavigationBar");

btnMenuOutline.addEventListener("click", function(){
    btnCloseOutline.style.display ="block";
    btnMenuOutline.style.display = "none";
    document.getElementById("sideNavigationBar").style.display ="block"
});

btnCloseOutline.addEventListener("click", function(){
    btnCloseOutline.style.display ="none";
    btnMenuOutline.style.display = "block";
    document.getElementById("sideNavigationBar").style.display ="none"
});


window.addEventListener("resize", () =>{
    if(window.innerWidth > 720){
        navMenu.style.display = "none";
        // btnCloseOutline.style.display = "none";
        // btnMenuOutline.style.display = "none";
    }
});
