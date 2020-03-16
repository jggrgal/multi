from reportlab.pdfgen import canvas
#----------------------------------------------------------------------
def createMultiPage():
    """
    Create a multi-page document
    """
    c = canvas.Canvas("canvas_page_num.pdf")
    
    for i in range(5):
        page_num = c.getPageNumber()
        text = "This is page %s" % page_num
        c.drawString(100, 750, text)
        c.showPage()
    c.save()
        
#----------------------------------------------------------------------
#if __name__ == "__main__":
createMultiPage()