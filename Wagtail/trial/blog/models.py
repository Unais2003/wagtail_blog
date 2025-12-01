from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from wagtail.snippets.models import register_snippet



@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Blog categories"



@register_snippet
class BlogAuthor(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    bio = RichTextField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('photo'),
        FieldPanel('bio'),
        FieldPanel('twitter'),
        FieldPanel('linkedin'),
    ]

    def __str__(self):
        return self.name



class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )



class BlogPage(Page):
    date = models.DateField("Post date")
    intro = RichTextField(blank=True)


    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )


    category = models.ForeignKey(
        'BlogCategory',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_posts'
    )


    author = models.ForeignKey(
        'BlogAuthor',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_posts'
    )


    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)


    body = StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('featured_image'),

       
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('category'),
            FieldPanel('tags'),
        ], heading="Post Metadata"),

        FieldPanel('body'),
    ]



class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # show only live, published BlogPage children
        context['posts'] = BlogPage.objects.child_of(self).live().order_by('-date')
        return context
