function fixPosition(){
    var toc = document.getElementById("toc")
    var toc_width = toc.offsetWidth;
    var container = document.getElementById("container");
    var cont_w = container.offsetWidth

    var width = window.innerWidth
    var offset_l = 0
    if (width > toc_width + cont_w){
        offset_l = (width - toc_width - cont_w) * 0.5
    }
    container.style.marginLeft = `${toc_width + offset_l}px`
    toc.style.left = offset_l.toString() + "px"
}

window.onresize = fixPosition