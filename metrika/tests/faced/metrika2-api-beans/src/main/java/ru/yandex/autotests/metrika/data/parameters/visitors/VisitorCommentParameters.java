package ru.yandex.autotests.metrika.data.parameters.visitors;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class VisitorCommentParameters extends VisitorInfoParameters {
    @FormParameter("comment")
    private String comment;

    public String getComment() {
        return comment;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }

    public VisitorCommentParameters withComment(String comment) {
        this.comment = comment;
        return this;
    }

    public static VisitorCommentParameters comment(String comment) {
        return new VisitorCommentParameters().withComment(comment);
    }
}
