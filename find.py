from poppler import load_from_file, PageRenderer
import cv2
import numpy
import multiprocessing

# where is the doc?
doc_path = "doc.pdf"
# in which resolution should we render the pages? The higher the resoltuion - the longer it is rendered
res = 150
# set to None to process all the pages.
# it takes too much time to render the pages to images, so i render only partially
pages_range = range(40, 70)
# basically useless. the size of the pool which was supposed to render pdf to images in parallel
pool_size = 8
# where is the image we will be looking for?
template_path = "part-1.png"
# in which sizes? Zoom does not work well, keep it smaller.
max_zoom = 3
scale_step = 0.9
total_steps = 20
scales = [max_zoom * pow(scale_step, x) for x in range(0, total_steps)]
# we search for template on each page. if the maximum score is this times bigger than
# the mean value of the rest of the pages - we consider a successful search.
limit = 3
# if the template is bigger than the image - cv2 crashes. so, lets not search for the images
# which are at least this times smaller than the page.
# if the page is 100x100 and this ratio is 4 - we will consider only sizes smaller than 25x25
min_ratio = 2

global pdf_document
pdf_document = load_from_file(doc_path)

def ProcessPage(pid):
    print("processing", pid)
    page = pdf_document.create_page(pid)
    renderer = PageRenderer()
    page_image = renderer.render_page(page, xres=res, yres=res,)
    page_numpy = numpy.uint8(numpy.array(page_image.memoryview(), copy=False))
    page_gs = cv2.cvtColor(page_numpy, cv2.COLOR_BGR2GRAY)
    return (pid, page_gs)

def ExtractImages(pages_range, res):
    if pages_range is None:
        pages_range = range(0, pdf_document.pages)
    pool = multiprocessing.Pool(pool_size)
    unordered_pages = pool.imap_unordered(ProcessPage, pages_range, 5)
    pages = {}
    for pid, page in unordered_pages:
        pages[pid] = page
    return pages

pages = ExtractImages(pages_range, res)

template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

for scale in scales:
    print("Checking", scale)
    scaled_template = cv2.resize(template, None, fx=scale, fy=scale)
    template_h, template_w = scaled_template.shape[-2:]
    print(scaled_template.shape)
    outs = []
    curr_max = 0
    max_loc = None
    sqr_loc = None
    for pid, page in pages.items():
        page_w, page_h = page.shape[-2:]
        if min_ratio * template_h > page_h or min_ratio * template_w > page_w:
            continue
        match_res = cv2.matchTemplate(page, scaled_template, cv2.TM_CCOEFF)
        _, maxv, _, max_l = cv2.minMaxLoc(match_res)
        outs.append(maxv)
        if maxv > curr_max:
            curr_max = maxv
            max_loc = pid
            sqr_loc = max_l
    if curr_max == 0:
        continue

    mean_v = numpy.mean(outs)
    print(mean_v / curr_max, "on page", max_loc + 1)
    if curr_max > limit * mean_v:
        print(sqr_loc)
        print("\n\nFound the template on the page ", max_loc + 1)
        pages[max_loc][sqr_loc[1]:sqr_loc[1]+template_h,sqr_loc[0]:sqr_loc[0]+1] = 0
        pages[max_loc][sqr_loc[1]:sqr_loc[1]+1,sqr_loc[0]:sqr_loc[0]+template_w] = 0
        pages[max_loc][sqr_loc[1]:sqr_loc[1]+template_h,sqr_loc[0]+template_w:sqr_loc[0]+template_w+1] = 0
        pages[max_loc][sqr_loc[1]+template_h:sqr_loc[1]+template_h+1,sqr_loc[0]:sqr_loc[0]+template_w+1] = 0
        cv2.imwrite("found_doc.png", pages[max_loc])
        print("See found_doc.png for the result.")
        cv2.imwrite("found_template.png", scaled_template)
        exit(0)

print("\n\nCould not find the template")
# image.save("page-42.png", "png")