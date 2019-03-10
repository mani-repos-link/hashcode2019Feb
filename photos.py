class Photo:
    def __init__(self, photo_id, landscape, tags):
        self.id = photo_id
        self.landscape = landscape
        self.tags = set(tags)  # breaks the string into an array
        self.is_framed = False  # checks whether is added to any slide or not

    def is_vertical(self):
        return self.landscape == "V"

    def is_horizontal(self):
        return self.landscape == "H"

    def get_total_tags(self):
        return len(self.tags)


class LoadPhotos:
    def __init__(self, filename):
        self.filename = filename
        self.photos = {}

    def read_file(self):
        file_in = open(self.filename, "r")
        file_in.readline()
        lines = file_in.readlines()

        self.photos = {}
        i = 0
        for line in lines:
            line = line.split()
            if len(line) <= 2:  # if any image does not have tags
                continue
            image_type = line[0]
            line = line[2:]
            self.photos[i] = (Photo(i, image_type, line))
            i += 1
        file_in.close()
        return self


class Slide:
    def __init__(self, photo_a, photo_b=None):
        self.photo = photo_a
        self.photoA = photo_a
        self.photoB = photo_b
        self.id = str(photo_a.id)
        self.tags = photo_a.tags
        self.set_photos()
        self.is_valid = True
        if photo_a.is_vertical() and photo_b is None:
            self.is_valid = False

    def set_photos(self):
        if self.photoB is not None:
            self.tags = self.tags.union(self.photoB.tags)
            self.id += " " + str(self.photoB.id)

    def get_slide_tags(self):
        return self.tags

    def get_id(self):
        return self.id

    def get_images(self):
        return [self.photoA, self.photoB]


def print_photos(photos):  # prints the photos id
    if type(photos) is dict:
        for p in photos:
            p = photos[p]
            #print("pid: ", p.id, "type: ", p.landscape, "tags: ", p.tags)
            print("pid:", p.get_id(), "tags:", p.tags)
    else:
        for p in photos:
            print("pid:", p.id, "type:", p.landscape, "tags: ", "len(", len(p.tags), ")", p.tags)


def get_vertical_photos(photos):
    v_photos = []
    for i in photos:
        if photos[i].is_vertical():
            v_photos.append(photos[i])
    v_photos.sort(key=lambda x: len(x.tags))
    return v_photos


def get_horizontal_photos(photos):
    h_photos = []
    for i in photos:
        if photos[i].is_horizontal():
            h_photos.append(photos[i])
    h_photos.sort(key=lambda x: len(x.tags))
    return h_photos


def get_horizontal_slides(photos):
    list_slides = []
    for p in photos:
        list_slides.append(Slide(p))
    return list_slides


def find_common(p1, p2):
    return len(p1.tags.intersection(p2.tags))


def get_matching_vertical_photo(index, photo, photos, accuracy=0):
    if accuracy == 0:
        accuracy = len(photos)

    v_photo = None
    tot_photos = len(photos)
    for i in range(tot_photos):
        i = i+index+1
        if tot_photos <= i:
            continue
        p1 = photos[i]
        if p1.is_horizontal() or p1.id == photo.id or p1.is_framed:
            continue

        if i >= accuracy:
            swap_list(photos, index+1, i)
            return p1

        v_photo = p1
        common = find_common(photo, p1)
        if common == 0:
            swap_list(photos, index+1, i)
            return p1
    return v_photo


def get_vertical_slides(v_photo_list, v_algo=0):
    slide_list = []
    i = -1
    p_ids = []
    v_photo_list.sort(key=lambda x: len(x.tags))
    print("Finding vertical images")
    if v_algo == 0:
        while len(v_photo_list)-1 > i:
            i += 1
            p1 = v_photo_list[i]
            if p1.is_framed:
                continue
            p2 = get_matching_vertical_photo(i, p1, v_photo_list, 0)
            # p2 = get_matching_vertical_photo(i, p1, v_photo_list, int(len(v_photo_list)/2)+1)
            if p2 is not None:
                slide_list.append(Slide(p1, p2))
                p1.is_framed = True
                p2.is_framed = True
                if p1.id in p_ids:
                    print("duplicate", p1.id)
                else:
                    p_ids.append(p1.id)
                if p2.id in p_ids:
                    print("duplicate", p2.id)
                else:
                    p_ids.append(p2.id)
                swap_list(v_photo_list, i + 1, v_photo_list.index(p2))
    else:
        p_len = len(v_photo_list)
        while (p_len/2) > 1+i:
            i += 1
            p1 = v_photo_list[i]
            p2 = v_photo_list[p_len - i-1]
            slide_list.append(Slide(p1, p2))
    return slide_list


def swap_list(_list, index_a, index_b):
    if len(_list) <= index_a or len(_list) <= index_b:
        return _list
    el = _list[index_a]
    _list[index_a] = _list[index_b]
    _list[index_b] = el
    return _list


def calculate_score(s1, s2):
    common = len(s1.tags.intersection(s2.tags))
    return min(common, (len(s1.tags) - common), (len(s2.tags) - common))


def slide_algo(slides, accuracy=10000):
    print("Starting algorithm")
    i, final_score, temp = 0, 0, 0
    while len(slides) > i:
        s1 = slides[i]
        index = i + 1
        j = 1
        max_score = -1
        while len(slides) > i + j:
            s2 = slides[i + j]
            if j > accuracy:
                break
            score = calculate_score(s1, s2)
            if score > max_score:
                index = i + j
                max_score = score
            j += 1

        final_score += max_score if max_score > 0 else 0
        if ((i+1) % 1000) == 0:
            print("i:", i, "finalScore", final_score, "accuracy", accuracy)
        slides = swap_list(slides, i + 1, index)
        i += 1
        temp += 1
        if (temp+1) % 1000 == 0:
            write_file(slides, temp)
    print("final score ", final_score)
    return slides, final_score


def write_file(slides, n=0, prepend_str="", file_name="outputs/ct_output.txt"):
    result = prepend_str
    if n == 0:
        n = len(slides)
    for slide in range(n):
        result += slides[slide].get_id() + "\n"
    result = str(n) + "\n" + result
    file_out = open(file_name, "w")
    try:
        file_out.write(result)
    except KeyboardInterrupt:
        print("exception")
    finally:
        file_out.close()


def runner(data_list: list):
    final_score = 0
    for data in data_list:
        filename = data[0]
        photos = LoadPhotos("input/" + filename).read_file().photos
        vertical_slides = get_vertical_slides(get_vertical_photos(photos))
        horizontal_slides = get_horizontal_slides(get_horizontal_photos(photos))
        slides = horizontal_slides + vertical_slides

        print(len(photos), "=> V slides:", len(vertical_slides), "H slides:", len(horizontal_slides), "Len:", len(slides))
        slides.sort(key=lambda x: len(x.tags))
        slides, f_s = slide_algo(slides, accuracy=data[1])
        final_score += f_s
        write_file(slides, file_name="outputs/" + filename)
        print("\n-----------\nfinal score", final_score, "\n\n")


# [ filename, accuracy, vertical_images_algorithm]
# accuracy = 0 - len(photos), the higher is accuracy the better result you get but it would take more time."""
# vertical_images_algorithm = [0,1]
#    0 => put v 2 photos in a slide whose 0 common tags,
#    1 => sort(v photos), then Slide(i , tot-1-i)

files = [
    ["a_example.txt", 4, 0],
    ["b_lovely_landscapes.txt", 1000, 0],  # only H photos
    ["c_memorable_moments.txt", 1000, 0],  # mix of V and H photos
    ["d_pet_pictures.txt", 1000, 0],  # mix of V and H photos
    ["e_shiny_selfies.txt", 1000, 0]  # only verticals
]

runner(files)
# score 702255 in 1-2h :-(
# score 406442 in 5-7min  with vertical algorithm 1 :-(
# score 404442 in 2-3min  with vertical algorithm 1 with accuracy 1 :-(
# score 404821 in 2min  with vertical algorithm 0 with accuracy 1 :-(
# score 818990 in 6min  with vertical algorithm 0 with accuracy 1000 :-(