# encoding: utf-8

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

def edge_factory(parent_model, child_model,
        parent_to_field="id", child_to_field="id", 
        concrete=True):
    
    class Edge(models.Model):
        class Meta:
            abstract = not concrete

        parent = models.ForeignKey(parent_model,
            related_name="%s_%s_child" % (child_model, parent_model), to_field=parent_to_field)
        child = models.ForeignKey(child_model,
            related_name="%s_%s_parent" % (child_model, parent_model), to_field=child_to_field)

        def __unicode__(self):
            return "%s points to %s" % (self.parent, self.child) 

    return Edge

# this is not in use yet, just an experiment
def generic_edge_factory(parent_model, child_model, 
        parent_id_field=models.PositiveIntegerField(), child_id_field=models.PositiveIntegerField(), 
        concrete=True):
    
    class Edge(models.Model):
        class Meta:
            abstract = not concrete

        parent_type = models.ForeignKey(ContentType)
        parent_id = parent_id_field
        parent = models.GenericForeignKey('parent_type', 'parent_id')
    
        child_type = models.ForeignKey(ContentType)
        child_id = child_id_field
        child = models.GenericForeignKey('child_type', 'child_id')
        
        def __unicode__(self):
            return "%s points to %s" % (self.parent, self.child) 

    return Edge


class AL_NodeBase(object):
    @classmethod
    def add_root(cls, **kwargs):
        cls(**kwargs).save()

    @classmethod
    def add_child(cls, **kwargs):
        raise NotImplementedError()

    @classmethod
    def add_sibling(cls, pos=None, **kwargs):
        raise NotImplementedError()

    """
    def delete(self, *vargs, **kwargs):
        # TODO: handle deletion of child nodes, 
        # but only if they have no other parents
        # (optionally with a keyword argument to force-delete all children
        # regardless of whether they have any other parents)
        return super(self.__class__, self).delete(*vargs, **kwargs)
    """
    
    @classmethod
    def get_tree(cls, parent=None):
        return [root.get_descendants() for root in cls.objects.filter(**{cls.parent_field: parent})]
        
    def get_depth(self):
        return (len(branch) for branch in self.get_ancestors())
    
    def get_max_depth(self):
        return max(self.get_depth())
    
    def get_min_depth(self):
        return min(self.get_depth())
            
    def get_tree_of_ancestors(self):
        # WARNING: this works the other way around: it starts from the parents 
        # and goes back to the ancestors
        parents = (self, [parent.get_tree_of_ancestors() for parent in self.parents.all()])
        return parents            
    
    # walk through ancestors as distinct branches of a tree (e.g. flatten the tree)
    def get_ancestors(self):
        # A queryset containing the current node object’s ancestors, starting by the root node 
        # and descending to the parent. (some subclasses may return a list)
        if self.is_root():
            return [[self]]
        else:
            branches = list()
            for parent in self.get_parents():
                for branch in parent.get_ancestors():
                    branch.append(self)
                    branches.append(branch)
            return branches

    
    def get_children(self):
        return self.child_field.all()    
    
    def get_children_count(self):
        return self.get_children().count()
        
    def get_tree_of_descendants(self):
        # recursion will stop on its own if the for loop has no more children to loop through
        children = (self, [child.get_tree_of_descendants() for child in 
                    self.__class__.objects.filter(**{self.parent_field: self.pk}).all()])
        return children
    
    def get_descendants(self):
        children = list()
        
        for child in self.get_children():
            children += [child]
            children += child.get_descendants()
        return children
        
    def get_descendants_count(self):
        return len(self.get_descendants())
        
    def get_first_child(self):
        return self.get_children()[0]

    def get_last_child(self):
        return self.get_children()[-1]
        
    def get_first_sibling(self):
        return self.get_siblings()[0]

    def get_last_sibling(self):
        return self.get_siblings()[-1]
        
    def get_prev_sibling(self):
        siblings = self.get_siblings()
        if siblings.index(self) > 0:
            return siblings[index - 1]
        else:
            return None

    def get_next_sibling(self):
        siblings = self.get_siblings()
        if siblings.index(self) < len(siblings) - 1:
            return siblings[index + 1]
        else:
            return None
    
    def get_parents(self):
        return self.parents.all()    

    # provided mainly to satisfy the Treebeard API, 
    # isn't very useful in itself
    def get_parent(self, update=False):
        return self.get_parents()[0]
    
    def get_root(self):
        if not self.is_root():
            return self.get_primary_parent().get_root()
        else:
            return self

    def get_siblings(self):
        siblings = list()
        for parent in self.get_parents():
            siblings += parent.get_children().all()
    
        # make sure no sibling is included twice (this can happen in acyclic graphs
        # because a child can share multiple parents with a sibling)
        return set(siblings)
        
    def is_child_of(self, node):
        return self in node.get_children()
        
    def is_descendant_of(self, node):
        # TODO: this method requires a flat representation of all descendants to search through
        raise NotImplementedError()
        
    def is_sibling_of(self, node):
        return self in node.get_siblings()

    def is_root(self):
        if not self.parents.count():
            return True
        else:
            return False
    
    def is_leaf(self):
        if not self.get_children().count():
            return True
        else:
            return False
            
    def move(self, target, pos=None):
        raise NotImplementedError()
    
    @classmethod
    def get_first_root_node(cls):
        return cls.get_root_nodes().order_by('pk')[0]

    @classmethod
    def get_last_root_node(cls):
        return cls.get_root_nodes().order_by('-pk')[0]
        
    @classmethod
    def get_root_nodes(cls):
        return cls.objects.filter(parents=None)

    @classmethod
    def load_bulk(cls, bulk_data, parent=None, keep_ids=False):
        raise NotImplementedError()
        
    @classmethod
    def dump_bulk(cls, parent=None, keep_ids=True):
        raise NotImplementedError()
    
    @classmethod
    def find_problems(cls):
        # e.g. cyclical graphs
        raise NotImplementedError()
        
    @classmethod
    def fix_problems(cls):
        raise NotImplementedError()
        
    @classmethod
    def get_descendants_group_count(parent=None):
        # Helper for a very common case: get a group of siblings and the 
        # number of descendants (not only children) in every sibling.
        raise NotImplementedError()

"""
Django's ORM is somewhat magical. We can't monkeypatch AL_Node
(e.g. do stuff like AL_Node.parents = models.ManyToManyField(...))
so we have put all functionality in a base class, and use a factory
to fill in the details of the Node model.
"""

def node_factory(edge_model):
    class AL_Node(models.Model, AL_NodeBase):
        class Meta:
            abstract = True
            
        parents = models.ManyToManyField('self', symmetrical=False, through=edge_model)

        parent_field = '%s_parent' % edge_model.__class__.__name__.lower()
        child_field = '%s_child' % edge_model.__class__.__name__.lower()

    return AL_Node