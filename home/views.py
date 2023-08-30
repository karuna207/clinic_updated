
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
import csv
from abc import ABC, abstractmethod
from datetime import datetime


# from LinkedQueue import LinkedQueue


class AbstractTree(ABC):
    """ Abstract Base Class for tree structure.
    Only five of the methods are abstract!
    Several concrete methods can be defined without
    knowing anything about the data structures for trees!!!
    Since the class is abstract, no objects can be created.
    """

    @abstractmethod
    def root(self):
        """ Returns the root (position) of this tree
        """

    @abstractmethod
    def parent(self, pos):
        """ Returns the parent of node at given position 'pos'.
        It is assumed that a valid position in this tree is given.
        """

    @abstractmethod
    def numChildren(self, pos):
        """ Returns the number of children of node at given position 'pos'.
        It is assumed that a valid position in this tree is given.
        """

    @abstractmethod
    def children(self, pos):
        """ Returns an iterator for the list of children of the node
        at given position 'pos'.
        It is assumed that a valid position in this tree is given.
        """

    @abstractmethod
    def __len__(self):
        """ Returns the total number of objects (nodes) in this tree.
        """

    def isRoot(self, pos):
        """ Returns `True' is the node at the given position `pos'
        is the root of this tree.
        It is assumed that a valid position in this tree is given.
        """
        return (pos == self.root())

    def isLeaf(self, pos):
        """ Returns `True' is the node at the given position `pos'
        is a leaf in this tree.
        It is assumed that a valid position in this tree is given.
        """
        return (self.numChildren(pos) == 0)

    def isEmpty(self):
        """ Returns `True' if this tree is empty.
        """
        return (len(self) == 0)

    def depthN(self, pos):
        """ Returns the depth of the node at the given position.
        Runs in linear time --- linear wrt the height --- O(h)
        """
        if self.isRoot(pos):
            return 0
        return 1 + self.depth(self.parent(pos))

    def _heightN(self, pos):
        """ Returns the height of the node at the given position.
        This is same as the height of the subtree rooted at `pos'.
        """
        if self.isLeaf(pos):
            return 0
        return 1 + max(self._heightN(child) for child in self.children(pos))

    def height(self, pos=None):
        """ Returns the height of the subtree rooted at `pos'.
        Returns the height of this tree, if `pos' is `None'.
        """
        if pos is None:
            if self.isEmpty():
                return -1  # By convention, height of empty tree is -1
            pos = self.root()
        return self._heightN(pos)

    def __iter__(self):
        """ Returns an iterator for this tree.
        This uses the iterator for positions in the tree.
        """
        for pos in self.positions():
            yield pos.getItem()

    def positions(self):
        """ Returns an iterator for positions in this tree.
        Uses the preorder traversal.
        """
        return self.preorder()

    def preorder(self):
        """ Returns the preorder iterator for positions in this tree.
        """
        if (not self.isEmpty()):
            for pos in self._preorderSubTree(self.root()):
                yield pos

    def _preorderSubTree(self, pos):
        """ Non-public recursive function used by the preorder iterator.
        """
        yield pos
        for child in self.children(pos):
            for p in self._preorderSubTree(child):
                yield p

    def postorder(self):
        """ Returns the postorder iterator for positions in this tree.
        """
        if (not self.isEmpty()):
            for pos in self._postorderSubTree(self.root()):
                yield pos

    def _postorderSubTree(self, pos):
        """ Non-public recursive function used by the postorder iterator.
        """
        for child in self.children(pos):
            for p in self._preorderSubTree(child):
                yield p
        yield pos

    # def breadthFirst(self):
    #     """ Returns the breadth-first iterator for positions in this tree.
    #     Uses a queue to keep track of all the paths in the tree.
    #     Space complexity is high compared to the depth-first iterators.
    #     """
    #     if ( not self.isEmpty() ):
    #         fringe = LinkedQueue()
    #         fringe.enqueue(self.root())
    #     while ( not fringe.isEmpty() ):
    #         pos = fringe.dequeue()
    #         yield pos
    #         for child in self.children(pos):
    #             fringe.enqueue(child)
# End of the class AbstractTree


class AbsBinaryTree(AbstractTree):
    """ An abstract base class for binary trees.
    This extends the abstract base class designed for general trees.
    One inherited abstract method (children) is overridden with a
    concrete implementation.
    Adds two abstract methods and a concrete method.
    """

    @abstractmethod
    def left(self, pos):
        """ Returns the left child of `pos' (if exists).
        Returns `None' is there is no left child.
        """

    @abstractmethod
    def right(self, pos):
        """ Returns the right child of `pos' (if exists).
        Returns `None' is there is no right child.
        """

    def children(self, pos):
        """ Returns an iterator for the list of children of the node
        at given position 'pos'.
        It is assumed that a valid position in this tree is given.
        """
        if (self.left(pos) is not None):
            yield self.left(pos)
        if (self.right(pos) is not None):
            yield self.right(pos)

    def sibling(self, pos):
        """ Returns the sibling of node at position `pos'.
        Returns `None' if `pos' does not have a sibling.
        It is assumed that a valid position in this tree is given.
        """
        parent = self.parent(pos)
        if parent is None:
            return None  # Self must be the root node
        if pos == self.left(parent):
            return self.right(parent)
        return self.left(parent)
# End of the class AbsBinaryTree


class LinkedBinaryTree(AbsBinaryTree):
    """ Concrete implementation of binary tree.
    Overrides all the abstract methods defined in the base classes.
    """

    class _historyNode:
        """ A nested class to define a binary tree node
        """

        # Let's explicity declare the fields
        # __slots__ = ['_item', '_parent', '_left', '_right']

        def __init__(self, pat_num, pat_his, pat_docass, parent=None, left=None, right=None):
            """ Constructs a new node with the given item
            """
            self.pat_num = pat_num
            self.pat_his = pat_his
            self.pat_docass = pat_docass
            self._parent = parent
            self._left = left
            self._right = right

        # def getItem(self):
        #     """ Accessor method to get the item stored in this node
        #     """
        #     return self._item

        # def setItem(self, item):
        #     """ Accessor method to modify the item stored in this node
        #     """
        #     self._item = item
    # End of nested class _BTNode

    # Fields of a tree object
    # __slots__ = ['_root', '_size']

    def __init__(self, pat_num=None, pat_his=None, pat_docass=None, TLeft=None, TRight=None):
        """ Construct a new empty binary tree, if no arguments are given.
        If only an item is given, a single node tree (containing that item)
        is created.
        """
        # First, construct an empty tree
        self._root = None  # This implementation does not use a dummy header
        self._size = 0
        # Add root and subtrees, if they are not None (and empty)
        if (pat_num is not None and pat_his is not None and pat_docass is not None):
            root = self.addRoot(pat_num, pat_his, pat_docass)
            # Add left subtree, if given
            if (TLeft is not None):
                # Ignore if TLeft is an empty tree
                if (TLeft._root is not None):
                    TLeft._root._parent = root
                    root._left = TLeft._root
                    self._size += TLeft._size
                    # Clear TLeft and make it an empty tree
                    TLeft._root = None
                    TLeft._size = 0
            # Add right subtree, if given
            if (TRight is not None):
                # Ignore if TRight is an empty tree
                if (TRight._root is not None):
                    TRight._root._parent = root
                    root._right = TRight._root
                    self._size += TRight._size
                    # Clear TRight and make it an empty tree
                    TRight._root = None
                    TRight._size = 0
    # End of the construtor for LinkedBinaryTree

    def root(self):
        """ Returns the root (position) of this tree.
        """
        return self._root

    def __len__(self):
        """ Returns the total number of objects (nodes) in this tree.
        """
        return self._size

    # def __str__(self):
        """ Returns a string representation of this tree.
        Uses the preorder traversal strategy.
        """
        # def __preorder(pos):
        #     res = f"[{pos._item} "
        #     if pos._left is not None:
        #         res += __preorder(pos._left)
        #     if pos._right is not None:
        #         res += __preorder(pos._right)
        #     res += ']'
        #     return res
        # if self._root is None:
        #     return '[]'
        # return __preorder(self._root)

    def parent(self, pos):
        """ Returns the parent of node at given position 'pos'.
        It is assumed that a valid position in this tree is given.
        """
        if pos is None:
            return None
        return pos._parent

    def numChildren(self, pos):
        """ Returns the number of children of node at given position 'pos'.
        It is assumed that a valid position in this tree is given.
        """
        count = 0
        if pos is None:
            return count
        if pos._left is not None:
            count += 1
        if pos._right is not None:
            count += 1
        return count

    def left(self, pos):
        """ Returns the left child of `pos' (if exists).
        Returns `None' is there is no left child.
        """
        if pos is None:
            return None
        return pos._left

    def right(self, pos):
        """ Returns the right child of `pos' (if exists).
        Returns `None' is there is no right child.
        """
        if pos is None:
            return None
        return pos._right

    def addRoot(self, pat_num, pat_his, pat_docass):

        if self._root is not None:
            raise ValueError("Root already exists!")
        self._root = self._historyNode(pat_num, pat_his, pat_docass)
        self._size = 1
        return self._root

    def addLeft(self, pat_num, pat_his, pat_docass, pos):
        if pos is None:
            raise TypeError("Not a valid position.")
        if pos._left is not None:
            raise ValueError("Left child already exists!")
        pos._left = self._historyNode(pat_num, pat_his, pat_docass, pos)
        self._size += 1
        return pos._left

    def addRight(self, pat_num, pat_his, pat_docass, pos):
        if pos is None:
            raise TypeError("Not a valid position.")
        if pos._right is not None:
            raise ValueError("Right child already exists!")
        pos._right = self._historyNode(pat_num, pat_his, pat_docass, pos)
        self._size += 1
        return pos._right

    # def replace(self, item, pos):
    #     if pos is None:
    #         raise TypeError("Not a valid position.")
    #     old = pos._item
    #     pos.setItem(item)
    #     return old
# End of class LinkedBinaryTree


class BinarySearchTree(LinkedBinaryTree):
    def __init__(self, pat_num=None, pat_his=None, pat_docass=None, Tleft=None, Tright=None):
        super().__init__(pat_num, pat_his, pat_docass, Tleft, Tright)

    def insert(self, pat_num, pathis, pat_doc, pos):

        if pat_num == pos.pat_num:
            pos.pat_his.extend(pathis)
        elif pat_num < pos.pat_num:
            if pos._left is None:
                pos._left = self.addLeft(pat_num, pathis, pat_doc, pos)
            else:
                self.insert(pat_num, pathis, pat_doc, pos._left)
        elif pat_num > pos.pat_num:
            if pos._right is None:
                pos._right = self.addRight(pat_num, pathis, pat_doc, pos)
            else:
                self.insert(pat_num, pathis, pat_doc, pos._right)

    def search(self, patnum, pos):
        print(pos)

        if patnum == pos.pat_num:
            return pos
        elif patnum < pos.pat_num and pos._left is not None:
            return self.search(patnum, pos._left)
        elif patnum > pos.pat_num and pos._right is not None:
            return self.search(patnum, pos._right)

    def findmax(self, pos=None):
        if pos is None:
            return pos._parent
        elif pos._right is not None:
            return self.findmax(pos._right)
        else:
            return pos

    def findmin(self, pos=None):
        if pos is None:
            return pos._parent
        elif pos.left is not None:
            return self.findmin(pos._left)
        else:
            return pos

    def delete(self, patnum):
        pos = self.search(patnum, self._root)

        parent = pos._parent
        if pos._left is None and pos._right is None:  # No children

            if parent._left == pos:
                parent._left = None
                self.size -= 1
                return
            elif parent.right == pos:
                parent.right = None
                self.size -= 1
        elif pos._left is not None and pos._right is None:  # one children - left
            parent._left = pos._left
            pos._parent = pos._left = pos._right = None
            self._size -= 1
        elif pos._right is not None and pos._left is None:  # one children - right
            parent._right = pos._right
            pos._parent = pos._left = pos._right = None
            self._size -= 1
        else:  # Two children
            r = self.findmin(pos._right)
            pos.pat_num = r.pat_num
            r.pat_num = 1000000
            self.delete(r.pat_num)


bstcsp = BinarySearchTree()
bstgendoc = BinarySearchTree()


class Patient_object:

    def __init__(self, p_name, p_age, p_emailid, p_gen, p_doc, p_num):
        self.p_name = p_name
        self.p_age = p_age
        self.p_emailid = p_emailid
        self.p_gen = p_gen
        self.p_doc = p_doc
        # self.date=date
        self.p_num = p_num


class queuepatientobject:
    def __init__(self, p_name, p_doc, p_num):
        self.patname = p_name
        self.doc = p_doc
        self.pnum = p_num


class Queue:
    def __init__(self, d_name):
        self.queue = []
        self.doc = d_name

    def enqueue(self, patient):
        self.queue.append(patient)

    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop(0)
        else:
            return None

    def emergency(self, patient):
        self.queue.insert(0, patient)

    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)


qcsp = Queue('csp')
qdoc = Queue('gendoc')


def home(request):
    return render(request, 'home.html')


def patient(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username.endswith('pat'):
            return redirect('home')

        if 'login' in request.POST:
            user = authenticate(username=username, password=password)

            # user_exists = User.objects.filter(username=username).exists()
            # password_exists = User.objects.filter(password=password).exists()
            # if user_exists==True and password_exists==True:
            #     return redirect('/patient/patientform')
            # else:
            #     return render(request, '/patient/patientlogin.html')
            print(user)
            if user is not None:
                login(request, user)
                return redirect('/patient/patientform')
            else:
                return render(request, r'D:\c++ course\python\clinic\templates\patientlogin.html')

        elif 'signup' in request.POST:
            if User.objects.filter(username=username).exists():
                # User with the given username already exists
                return render(request, r'D:\c++ course\python\clinic\templates\response2.html')
            else:
                user = User.objects.create_user(
                    username=username, password=password)
                return redirect('/patient/patientform')

    else:
        return render(request, 'patientlogin.html')


def doctor(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username.endswith('doc'):
            return redirect('home')

        if 'login' in request.POST:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if username == 'sridharandoc':
                    return redirect('/doctor/doctorcsphome')
                elif username == 'vijayalakshmidoc':
                    return redirect('/doctor/doctorgendochome')
            else:
                return render(request, r'D:\c++ course\python\clinic\templates\doctorlogin.html')

        # elif 'signup' in request.POST:
        #     if User.objects.filter(username=username).exists():
        #         # User with the given username already exists
        #         return HttpResponse('Username already exists')
        #     else:
        #         user = User.objects.create_user(username=username, password=password)
        #         return redirect('/receptionist')
    return render(request, 'doctorlogin.html')


def receptionist(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username.endswith('rep'):
            return redirect('home')

        if 'login' in request.POST:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/receptionist/recephome')
            else:
                return render(request, 'receptionistlogin.html')

        # elif 'signup' in request.POST:
        #     if User.objects.filter(username=username).exists():
        #         # User with the given username already exists
        #         return HttpResponse('Username already exists')
        #     else:
        #         user = User.objects.create_user(username=username, password=password)
        #         return redirect('/receptionist/recephome')
    return render(request, 'receptionistlogin.html')


def makeappointment(request):
    if request.method == 'POST':
        if 'submit' in request.POST:

            pat_name = request.POST.get('p_name')
            pat_age = request.POST.get('p_age')
            pat_emailid = request.POST.get('p_emailid', '--gmail.com')
            patgen = request.POST.get('p_gen', None)
            # female_option = request.POST.get('p_gen', None)
            # others_option = request.POST.get('p_gen', None)
            # patgen=None
            # if male_option:
            #     patgen='male'
            # if female_option:
            #     patgen='female'
            # if others_option:
            #     patgen='others'
            doctor_ass = request.POST.get('doc_ass', None)
            pat_num = request.POST.get('p_num')
            pat_sym = request.POST.get('symptoms')
            currentdate = datetime.today().date()
            pat_sym = [pat_sym+','+str(currentdate)]

            # doctor_ass stores either csp or gendoc
            # date=datetime.date.today()
            p_obj = Patient_object(
                pat_name, pat_age, pat_emailid, patgen, doctor_ass, pat_num)
            if p_obj.p_doc == 'csp':
                fr = open(
                    r'D:\c++ course\python\clinic\appointment\appointmentcsp.csv', 'r')
                reader = csv.reader(fr)
                reader = list(reader)
                print(len(reader))
                # if len(reader)!=1:
                #     for i in reader:
                #         if i[5]==pat_num:
                #             return render(
                #             request,
                #             r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                #             {"alertmessage": "you have already booked an appointment!"},
                #         ) 
                #         else:
                #             pass
                        
                if len(reader) < 3:

                    fw = open(
                        r'D:\c++ course\python\clinic\appointment\appointmentcsp.csv', 'a', newline="")
                    writer = csv.writer(fw)
                    data = [pat_name, pat_age, pat_emailid,
                            patgen, doctor_ass, pat_num]
                    writer.writerow(data)

                    fw.close()
                    if len(bstcsp) == 0:
                        bstcsp.addRoot(pat_num, pat_sym, doctor_ass)
                        print('hi')
                    else:
                        k = bstcsp.search(pat_num, bstcsp._root)
                        if k is None:
                            bstcsp.insert(pat_num, pat_sym,
                                          doctor_ass, bstcsp._root)
                            print('again')
                        else:
                            k.pat_his.extend(pat_sym)
                else:
                    return render(
                        request,
                        r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                        {"alertmessage": "appointments are filled!"},
                    )

            elif p_obj.p_doc == 'gendoc':
                fr = open(
                    r'D:\c++ course\python\clinic\appointment\appointmentgendoc.csv', 'r')
                reader = csv.reader(fr)
                reader = list(reader)
                # if len(reader)!=0:
                #     for i in reader:
                #         if i[5]==pat_num:
                #             return render(
                #             request,
                #             r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                #             {"alertmessage": "you have already booked an appointment!"},
                #         ) 
                #         else:
                #             pass
                if len(reader) < 3:

                    fw = open(
                        r'D:\c++ course\python\clinic\appointment\appointmentgendoc.csv', 'a', newline="")
                    data = [pat_name, pat_age, pat_emailid,
                            patgen, doctor_ass, pat_num]
                    writer = csv.writer(fw)
                    writer.writerow(data)
                    fw.close()
                    if len(bstgendoc) == 0:
                        bstgendoc.addRoot(pat_num, pat_sym, doctor_ass)
                    else:
                        bstgendoc.insert(pat_num, pat_sym,
                                         doctor_ass, bstgendoc._root)
                else:
                    return render(
                        request,
                        r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                        {"alertmessage": "appointments are filled!"},
                    )

            # fr=open(r'D:\c++ course\python\clinic\appointment\history.csv','r')
            # reader=csv.reader(fr)
            # tot_data=list(reader)
            # for data in tot_data:
            #     if data[-2]==pat_num and data[-3]==doctor_ass:
            #         data[-1].append(pat_sym)
            #         break
            # else:
            #     tot_data.append([pat_name,pat_emailid,patgen,doctor_ass,pat_num,pat_sym])

            # fr.close()

            # f=open(r'D:\c++ course\python\clinic\appointment\history.csv','w')
            # writer=csv.writer(f)
            # for data in tot_data:
            #     writer.writerow(data)
            # f.close()
            # if doctor_ass=='csp':
            #     if len(bstcsp)==0:
            #         bstcsp.addRoot(pat_num,pat_sym,doctor_ass)
            #         print('hi')
            #     else:
            #         bstcsp.insert(pat_num,pat_sym,doctor_ass,bstcsp._root)
            #         print('again')
            elif doctor_ass == 'gendoc':
                if len(bstgendoc) == 0:
                    bstgendoc.addRoot(pat_num, pat_sym, doctor_ass)
                else:
                    bstgendoc.insert(pat_num, pat_sym,
                                     doctor_ass, bstgendoc._root)

            return render(request, r'D:\c++ course\python\clinic\templates\response1.html')
    return render(request, 'patient-form.html')


def addpatienttoqueue(request):
    if request.method == 'POST':

        if 'submit' in request.POST:
            pat_name = request.POST.get('p_name')
            # pat_age=request.POST.get('p_age')
            # pat_emailid=request.POST.get('p_emailid','--gmail.com')
            # male_option = request.POST.get('p_male', None)
            # female_option = request.POST.get('p_female', None)
            # others_option = request.POST.get('p_others', None)
            # patgen=None
            # if male_option:
            #     patgen='male'
            # if female_option:
            #     patgen='female'
            # if others_option:
            #     patgen='others'
            doctor_ass = request.POST.get('doc_ass', None)
            pat_num = request.POST.get('p_num')

            if doctor_ass == 'csp':
                f = open(
                    r'D:\c++ course\python\clinic\appointment\appointmentcsp.csv', 'r', newline="")
                reader = csv.reader(f)
                reader = list(reader)
                try:
                    for row in reader:
                        if row[0] == pat_name and row[-1] == pat_num:
                            pat_obj = queuepatientobject(
                                pat_name, doctor_ass, pat_num)
                            qcsp.enqueue(pat_obj)
                            return render(
                                request,
                                r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                                {"alertmessage": "appointment found you can wait in the queue!"},
                            )
                            break
                    else:

                        return render(
                            request,
                            r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                            {"alertmessage": "appointment not found!"},
                        )
                except:
                    return render(
                        request,
                        r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                        {"alertmessage": "appointment not found!"},
                    )

                f.close()

            elif doctor_ass == 'gendoc':
                f = open(
                    r'D:\c++ course\python\clinic\appointment\appointmentgendoc.csv', 'r', newline="")
                reader = csv.reader(f)
                reader = list(reader)
                try:
                    for row in reader:
                        print(row)
                        # if len(row) ==0:
                        #     return render(
                        #     request,
                        #     r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                        #     {"alertmessage": "appointment not found!"},
                        #     )
                        if row[0] == pat_name and row[-1] == pat_num:
                            pat_obj = queuepatientobject(
                                pat_name, doctor_ass, pat_num)
                            qdoc.enqueue(pat_obj)
                            return render(
                                request,
                                r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                                {"alertmessage": "appointment  found  you can wait in the queue!"},
                            )
                            break

                    else:
                        print('a')
                        return render(
                            request,
                            r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                            {"alertmessage": "appointment not found!"},
                        )
                except:
                    return render(
                        request,
                        r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                        {"alertmessage": "appointment not found!"},
                    )

                f.close()

    return render(request, 'addpatqueue.html')


def emergency(request):
    if request.method == 'POST':

        if 'submit' in request.POST:
            pat_name = request.POST.get('p_name')
            doctor_ass = request.POST.get('doc_ass', None)
            pat_num = request.POST.get('p_num')

            if doctor_ass == 'csp':

                pat_obj = queuepatientobject(pat_name, doctor_ass, pat_num)
                qcsp.emergency(pat_obj)
                return render(request,
                              r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                              {"alertmessage": "you can wait in the queue!"},
                              )

            elif doctor_ass == 'gendoc':

                pat_obj = queuepatientobject(pat_name, doctor_ass, pat_num)
                qdoc.emergency(pat_obj)
                return render(
                    request,
                    r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                    {"alertmessage": " you can wait in the queue!"},
                )

    return render(request, 'emergency.html')


def addpat(request):
    return render(request, 'addpatqueue.html')


def recephome(request):
    return render(request, r'D:\c++ course\python\clinic\templates\recp.html')


def doccsphome(request):
    return render(request, r'D:\c++ course\python\clinic\templates\doctorcsphome.html')


def gendochome(request):
    return render(request, r'D:\c++ course\python\clinic\templates\doctorgendoc.html')


def patientcsphistory(request):
    if request.method != 'POST':
        return render(request, r'D:\c++ course\python\clinic\templates\searchhistorycsp.html')
    else:
        if 'submit' in request.POST:

            pat_num = request.POST.get('p_num')

            # print(bstcsp._root.pat_num)
            if bstcsp._root is not None:
                pos = bstcsp.search(pat_num, bstcsp._root)

                if pos == None:
                    return render(request,
                              r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                              {"alertmessage": f'{pat_num} history not found'},
                              )
                    
                else:
                    # return HttpResponse(f'this is the history of patient :{pos.pat_his}')
                    context={'des':pos.pat_his,'k':0}
                
                    return render(request,'patienthistoryviewcsp.html',context)
            else:
                return render(request,
                              r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                              {"alertmessage": f'{pat_num} history not found'},
                              )
                

def presriptioncsp(request):
    if request.method != 'POST':
        return render(request, r'D:\c++ course\python\clinic\templates\prescriptioncsp.html')
    else:
        if 'submit' in request.POST:

            pat_num = request.POST.get('p_num')
            pat_sym=request.POST.get('p_problems')
            currentdate=datetime.today().date()
            pat_pre=request.POST.get('Prescription')
            doctor_ass='csp'
            pat_sym=[pat_sym+' '+pat_pre+','+str(currentdate)]
            k = bstcsp.search(pat_num, bstcsp._root)
            if k is None:
                bstcsp.insert(pat_num, pat_sym,doctor_ass, bstcsp._root)
                print('again')
            else:
                popped=k.pat_his.pop()
                k.pat_his.extend(pat_sym) 
            return render(request,
                              r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                              {"alertmessage": "medical history has been updated!"},
                              ) 
        
def presriptiongendoc(request):
    if request.method != 'POST':
        return render(request, r'D:\c++ course\python\clinic\templates\prescriptiongendoc.html')
    else:
        if 'submit' in request.POST:

            pat_num = request.POST.get('p_num')
            pat_sym=request.POST.get('p_problems')
            currentdate=datetime.today().date()
            pat_pre=request.POST.get('Prescription')
            doctor_ass='gendoc'
            pat_sym=[pat_sym+' '+pat_pre+','+str(currentdate)]
            k = bstgendoc.search(pat_num, bstgendoc._root)
            if k is None:
                bstgendoc.insert(pat_num, pat_sym,doctor_ass, bstgendoc._root)
                print('again')
            else:
                popped=k.pat_his.pop()
                k.pat_his.extend(pat_sym) 
            return render(request,
                              r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                              {"alertmessage": "medical history has been updated!"},
                              ) 
                 
        



            # print(bstcsp._root.pat_num)
            # if bstcsp._root is not None:
            #     pos = bstcsp.search(pat_num, bstcsp._root)

            #     if pos == None:
            #         # return HttpResponse(f'{pat_num} history not found')
            #     else:
            #         return HttpResponse(f'this is the history of patient :{pos.pat_his}')
            # else:
            #     return HttpResponse(f'{pat_num} history not found')
            
            # self.insert(pat_num, pathis, pat_doc, pos._right)
    

def clearappointments(request):
    fw = open(r'D:\c++ course\python\clinic\appointment\appointmentcsp.csv', 'w')
    fw.close()
    fw = open(r'D:\c++ course\python\clinic\appointment\appointmentgendoc.csv', 'w')
    fw.close()
    return render(request,
                  r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                  {"alertmessage": "all appointments made today are cancelled!"},
                  )


def patientgendochistory(request):
    if request.method != 'POST':
        return render(request, r'D:\c++ course\python\clinic\templates\searchhistorygendoc.html')
    else:
        if 'submit' in request.POST:

            pat_num = request.POST.get('p_num')

            if bstgendoc._root is not None:
                pos = bstgendoc.search(pat_num, bstgendoc._root)

                if pos == None:
                    return render(request,
                              r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                              {"alertmessage": f'{pat_num} history not found'},
                              )
                else:
                    # return HttpResponse(f'this is the history of patient :{pos.pat_his}')
                    context={'des':pos.pat_his}
                
                    return render(request,'patienthistoryviewgendoc.html',context)
            else:
                return render(request,
                              r'D:\c++ course\python\clinic\templates\removepatientdisplay.html',
                              {"alertmessage": f'{pat_num} history not found'},
                              )


def showcspqueuetodoc(request):
    context = {}
    i = 0
    for detail in qcsp.queue:
        i += 1
        context[i] = detail

    return render(request, "queuedetailcsp.html", {"result": context})


def showgendocqueue(request):
    context = {}
    i = 0
    for detail in qdoc.queue:
        i += 1
        context[i] = detail

    return render(request, "queuedetailgendoc.html", {"result": context})


def showqueuecsp(request):
    context = {}
    i = 0
    for detail in qcsp.queue:
        i += 1
        context[i] = detail

    return render(request, "queuedetailcsp.html", {"result": context})


def showqueuegendoc(request):
    context = {}
    i = 0
    for detail in qdoc.queue:
        i += 1
        context[i] = detail

    return render(request, "queuedetailgendoc.html", {"result": context})


def dequeuegendoc(request):
    rem_patient = qdoc.dequeue()
    if rem_patient != None:
        return (render(request, r'D:\c++ course\python\clinic\templates\removepatientdisplay.html', {"alertmessage": f"{rem_patient.patname} can meet {rem_patient.doc}"}))

    else:
        return render(request, r'D:\c++ course\python\clinic\templates\response3.html')


def dequeuecsp(request):
    rem_patient = qcsp.dequeue()
    if rem_patient != None:
        return render(request, r'D:\c++ course\python\clinic\templates\removepatientdisplay.html', {"alertmessage": f"{rem_patient.patname} can meet {rem_patient.doc}"})
    else:
        return render(request, r'D:\c++ course\python\clinic\templates\response3.html')


# def makepayment(request):
#     return render(request,)


# import csv

# def makeappointment(request):
#     if request.method == 'POST':
#         pat_name = request.POST.get('p_name')
#         pat_age = request.POST.get('p_age')
#         pat_emailid = request.POST.get('p_emailid')
#         pat_gender = request.POST.get('p_gender')
#         doctor_ass = request.POST.get('doc_ass')
#         pat_num = request.POST.get('p_num')
#         date = datetime.date.today()

#         p_obj = Patient_object(pat_name, pat_age, pat_emailid, pat_gender, doctor_ass, date, pat_num)

#         # Define the CSV file path
#         csv_file_path = 'appointmentcsp.csv'

#         # Open the CSV file in append mode
#         with open(csv_file_path, 'a', newline='') as f:
#             writer = csv.writer(f)

#             # Write the patient data as a new row in the CSV file
#             writer.writerow([p_obj.p_name, p_obj.p_age, p_obj.p_emailid, p_obj.p_gen, p_obj.p_doc, p_obj.date, p_obj.p_num])

#         return HttpResponse('Appointment made successfully')

#     return render(request, 'patient-form.html')

        # if len()==0:
        #     qcsp=Queue('csp')
        #     qgdoc=Queue('gendoc')
        #     if p_obj.p_doc=='csp':
        #         qcsp.enqueue(p_obj)
        #     else:
        #         qgdoc.enqueue(p_obj)

        #     f.close()
        #     fw=open(r'D:\c++ course\python\clinic\appointment\appointment.txt','w')
        #     fw.writelines(['{qcsp}\n','{qgdoc}'])
        #     fw.close()
        # else:
        #     listofqueue=f.read().split('\n')
        #     qcsp=listofqueue[0]
        #     qgdoc=listofqueue[1]


# def my_view(request):
#     if request.method == 'POST':
#         selected_option = request.POST.get('radio_button_name', None)
#         if selected_option:
#             # Do something based on the selected_option
#             print(f"The selected option is: {selected_option}")
#         else:
#             # No option was selected
#             print("No option selected")

    # Rest of your view logic
    # ...


# Create your views here.
# def my_view(request):
#     if request.method == 'POST':
#         selected_option = request.POST.get('select_name', None)
#         if selected_option:
#             # Do something based on the selected_option
#             print(f"The selected option is: {selected_option}")
#         else:
#             # No option was selected
#             print("No option selected")

    # Rest of your view logic
    # ...

# from django.shortcuts import render,HttpResponse,redirect
# from django.contrib.auth.models import User
# from django.contrib.auth import logout,authenticate,login

# def home(request):
#     return render(request,'home.html')


# def patient(request):

#     if request.method=="POST":
#         username=request.POST.get('username')
#         password=request.POST.get('password')
#         if username.endswith('pat')!=True:
#             return redirect('home')
#         if 'login' in request.POST:
#             user=authenticate(username=username,password=password)
#             if user is not None:
#                 login(request,user)
#                 return redirect("home:patient/form")
#             else:
#                 return render(request,'patientlogin.html')

#         elif 'signup' in request.POST:
#             # Sign up button was clicked
#             # Process the sign up logic here
#             user = User.objects.create_user(username=username, password=password)
#             return redirect("/patient/form")


#     else:
#         return render(request,'patientlogin.html')

# def doctor(request):
#     return render(request,'doctorlogin.html')

# def receptionist(request):
#     return render(request,'receptionistlogin.html')

# def patientform(request):
#     return render(request,'patient-form.html')
# f=open(r'D:\c++ course\python\clinic\appointment\appointmentcsp.csv','r',newline="")
        # reader=csv.reader(f)
        # data=list(reader)
        # print(data)
        # if len(data)!=0:

        #     print(data)
        #     data.append([pat_name,pat_age,pat_emailid,patgen,doctor_ass,pat_num])
        #     print(data)

        # else:
        #     data=[pat_name,pat_age,pat_emailid,patgen,doctor_ass,pat_num]
