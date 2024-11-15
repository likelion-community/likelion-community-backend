from django.contrib import admin
from .models import *

# PostImage 모델 어드민 클래스
class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1  # 이미지 추가 시 기본으로 표시되는 빈 폼 수

    # 이미지 미리 보기를 위한 메서드
    def image_preview(self, obj):
        if obj.image:
            return '<img src="{}" style="width: 100px; height: auto;" />'.format(obj.image.url)
        return "(No Image)"
    image_preview.allow_tags = True
    image_preview.short_description = "Image Preview"
    fields = ['image', 'image_preview']
    readonly_fields = ['image_preview']

# MainBoard 어드민 클래스
class MainBoardAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]  # 인라인으로 PostImage 추가
    list_display = ['id', 'title', 'writer', 'time', 'likes_count', 'scraps_count']
    readonly_fields = ['likes_count', 'scraps_count', 'comments_count']

    # 댓글 수 표시 메서드
    def comments_count(self, obj):
        return obj.comments_count()
    
    # 좋아요 수 표시 메서드
    def likes_count(self, obj):
        return obj.likes_count()
    
    # 스크랩 수 표시 메서드
    def scraps_count(self, obj):
        return obj.scraps_count()

# SchoolBoard 어드민 클래스
class SchoolBoardAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]
    list_display = ['id', 'title', 'writer', 'time', 'likes_count', 'scraps_count']
    readonly_fields = ['likes_count', 'scraps_count', 'comments_count']

    def comments_count(self, obj):
        return obj.comments_count()

    def likes_count(self, obj):
        return obj.likes_count()
    
    def scraps_count(self, obj):
        return obj.scraps_count()

# QuestionBoard 어드민 클래스
class QuestionBoardAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]
    list_display = ['id', 'title', 'writer', 'time', 'likes_count', 'scraps_count']
    readonly_fields = ['likes_count', 'scraps_count', 'comments_count']

    def comments_count(self, obj):
        return obj.comments_count()

    def likes_count(self, obj):
        return obj.likes_count()
    
    def scraps_count(self, obj):
        return obj.scraps_count()

# 모델 어드민 등록
admin.site.register(MainBoard, MainBoardAdmin)
admin.site.register(SchoolBoard, SchoolBoardAdmin)
admin.site.register(QuestionBoard, QuestionBoardAdmin)
admin.site.register(MainComment)
admin.site.register(SchoolComment)
admin.site.register(QuestionComment)
admin.site.register(MainNoticeBoard)
admin.site.register(SchoolNoticeBoard)
admin.site.register(MainNoticeComment)
admin.site.register(SchoolNoticeComment)
admin.site.register(PostImage)  # PostImage 모델 직접 등록
